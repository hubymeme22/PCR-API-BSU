from flask import request
from app.database.models import Accounts, Campuses, OPCR
from app.modules import ErrorGen, Sessions
from bson.objectid import ObjectId
import json

# returns all the account info from the database
# excluding the password
def adminAccount():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    accounts = Accounts.objects().to_json()
    return {
        'data': json.loads(accounts),
        'error': None
    }

# retrieve all head accounts
def adminHeadAccount():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    accounts = Accounts.objects(permission='head').to_json()
    return {
        'data': json.loads(accounts),
        'error': None
    }

# retrieve all head accounts
def adminUnassignedHeadAccount():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    campuses = Campuses.objects()
    accounts = json.loads(Accounts.objects(permission='head').to_json())

    # super ultra mega slow manual bruteforce (my bad)
    existingHeadIDs = []
    for campus in campuses:
        for office in campus['offices']:
            if (office['head'] != ''):
                existingHeadIDs.append(office['head'])

    # search if the current account's id already exists
    notRegisteredHead = []
    for headAccount in accounts:
        if (headAccount['_id']['$oid'] not in existingHeadIDs):
            notRegisteredHead.append(headAccount)

    return {
        'data': notRegisteredHead,
        'error': None
    }

# returns the account info from the database where user
# having the spcified id
def adminAccountWithID(id):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    account = Accounts.objects(id=id).first().to_json()
    return {
        'data': json.loads(account),
        'error': None
    }

def adminDeleteAccountWithID(id):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    account = Accounts.objects(id=id).first()
    if (account == None): return ErrorGen.invalidRequestError(error='NonexistentAccount', statusCode=400)

    account.delete()
    return {
        'data': None,
        'deleted': True,
        'error': None
    }

# assigns individual to head as superior
def adminAssignSuperior(headid, individ):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    # checks if the accounts really do exist
    headAccount = Accounts.objects(id=headid, permission='head').first()
    if (headAccount == None): return ErrorGen.invalidRequestError(error='NonexistentAccount', statusCode=404)

    indivAccount = Accounts.objects(id=individ, permission='individual').first()
    if (indivAccount == None): return ErrorGen.invalidRequestError(error='NonexistentAccount', statusCode=404)

    # assign the superior of indiv as the head
    indivAccount.update(superior=headid)
    return {
        'data': None,
        'updated': True,
        'error': None
    }

# creates a new account for PMT
def adminCreateAccountPMT():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    accountDetails = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'username', 'email', 'password'],
        jsonRequest=accountDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    new_account = Accounts(
        name = accountDetails['name'],
        username=accountDetails['username'],
        email=accountDetails['email'],
        password=accountDetails['password'],
        superior = accountDetails.get('superior'),
        permission='pmt'
    )

    new_account.save()
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'pmt',
        'error': None
    }

# creates a new account for office head
def adminCreateAccountHead():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    accountDetails = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'username', 'email', 'password'],
        jsonRequest=accountDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    new_account = Accounts(
        name = accountDetails['name'],
        username=accountDetails['username'],
        email=accountDetails['email'],
        password=accountDetails['password'],
        permission='head'
    )
    new_account.save()
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'head',
        'error': None
    }


# creates a new account for office individuals
def adminCreateAccountIndiv():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    accountDetails = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'username', 'email', 'password', 'superior'],
        jsonRequest=accountDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    new_account = Accounts(
        name = accountDetails['name'],
        username=accountDetails['username'],
        email=accountDetails['email'],
        password=accountDetails['password'],
        permission='individual'
    )
    new_account.save()
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'indv',
        'error': None
    }

# creates and registers new campus
def adminCreateCampus():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    campusDetails: dict = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'offices'],
        jsonRequest=campusDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    # automatically set the head value to empty string
    for i in range(len(campusDetails['offices'])):
        office = campusDetails['offices'][i]
        if ('head' not in office):
            campusDetails['offices'][i].update({'head': ''})

    # initialize the list of pmt ids as empty
    campusDetails.update({'pmt': []})
    newCampus = Campuses(**campusDetails)
    newCampus.save()

    return {
        'id': str(newCampus.id),
        'created': True,
        'error': None
    }

# assigns the pmt to a specific campus
def adminAssignPmtCampus():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    campusDetails = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['campus', 'pmtid'],
        jsonRequest=campusDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    # checks if the pmt has already campus assigned
    otherCampuses = Campuses.objects(pmt__in=campusDetails['pmtid']).first()
    if (otherCampuses != None):
        return ErrorGen.invalidRequestError(error='CampusAlreadyAssigned', statusCode=403)

    # assign the pmt to campus
    otherCampuses = Campuses.objects(id=campusDetails['campus']).first()
    if (otherCampuses == None):
        return ErrorGen.invalidRequestError(error='NonexistentCampus', statusCode=403)

    otherCampuses.pmt.append(campusDetails['pmtid'])
    otherCampuses.save()

    return {
        'data': json.loads(otherCampuses.to_json()),
        'error': None
    }

# assigns a head to a specific department
def adminAssignHeadCampus():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    requestPayload = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['campusid', 'departmentid', 'headid'],
        jsonRequest=requestPayload)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    # retrieve the campus specified
    campusData = Campuses.objects(id=requestPayload['campusid']).first()
    if (campusData == None): return ErrorGen.invalidRequestError(error='NonexistentCampus')

    # retrieve the specific department
    parsedCampusData = json.loads(campusData.to_json())
    departmentIndex = -1
    for i in range(len(parsedCampusData['offices'])):
        if (requestPayload['departmentid'] == parsedCampusData['offices'][i]['_id']['$oid']):
            departmentIndex = i
            break

    if (departmentIndex < 0):
        return ErrorGen.invalidRequestError(error='NonexistentDepartment')

    # convert the office object ids into ObjectID
    for i in range(len(parsedCampusData['offices'])):
        parsedCampusData['offices'][i]['_id'] = ObjectId(parsedCampusData['offices'][i]['_id']['$oid'])

    # unoptimized krazy code
    unassignedAccounts = adminUnassignedHeadAccount()
    for account in unassignedAccounts['data']:
        if (account['_id']['$oid'] == requestPayload['headid']):
            parsedCampusData['offices'][departmentIndex]['head'] = requestPayload['headid']
            campusData.update(offices=parsedCampusData['offices'])
            return {
                'data': '',
                'assigned': True,
                'error': None
            }

    return ErrorGen.invalidRequestError(error='AccountAlreadyAssigned')

# retrieves all the campuses
def adminGetCampuses():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    campuses = Campuses.objects()
    return {
        'data': json.loads(campuses.to_json()),
        'error': None
    }

# retrieves all departments in a campus
def adminGetDepartments(campusid):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    campuses = Campuses.objects(id=campusid).first()
    if (campuses == None): return ErrorGen.invalidRequestError(error='NonexistentCampus')

    campusData = json.loads(campuses.to_json())
    return {
        'data': campusData['offices'],
        'error': None
    }


# deletes office data and remove the office head access
def adminDeleteOffice(campusid, departmentid):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    campuses = Campuses.objects(id=campusid).first()
    if (campuses == None): return ErrorGen.invalidRequestError(error='NonexistentCampusID', statusCode=404)

    parsedCampuses: dict = json.loads(campuses.to_json())
    retrievedOffices: list[dict] = parsedCampuses['offices']

    # manually search for the matched id and deletes it
    departmentFound = False
    for i in range(len(retrievedOffices)):
        office = retrievedOffices[i]
        if (office['_id']['$oid'] == departmentid):
            retrievedOffices.pop(i)
            departmentFound = True
            break

    if (not departmentFound):
        return ErrorGen.invalidRequestError(error='NonexistentDepartmentID')

    # manually update the list with valid object id
    updatedOfficeList = []
    for i in range(len(retrievedOffices)):
        office = retrievedOffices[i]
        office.update({ '_id': ObjectId(office['_id']['$oid']) })
        updatedOfficeList.append(office)

    # update on the database part
    campuses.update(offices=updatedOfficeList)
    return {
        'data': {},
        'updated': True,
        'error': None
    }

# edits the campus data (add new department/office)
def adminEditCampusData(campusid):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    # check if the campus exist in the database
    campus = Campuses.objects(id=campusid).first()
    if (campus == None): return ErrorGen.invalidRequestError(error='NonexistentCampus')

    # retrieve and check parameters
    campusData = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(['name', 'offices'], campusData)
    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    # check every office parameters
    for officeData in campusData['offices']:
        missedOfficeParam = ErrorGen.parameterCheck(['name', 'head', 'opcr'], officeData)
        if (len(missedOfficeParam) > 0):
            return ErrorGen.invalidRequestError(error=f'MissedParams={missedOfficeParam}')

    # if existing opcr is passed alongside with old opcr
    # convert the id into valid id format
    for i in range(len(campusData['offices'])):
        officeData = campusData['offices'][i]
        if ('_id' in officeData):
            campusData['offices'][i]['_id'] = ObjectId(officeData['_id']['$oid'])

        if ('id' in officeData):
            campusData['offices'][i]['id'] = ObjectId(officeData['id'])

    # campuses update
    campus.update(name=campusData['name'], offices=campusData['offices'])
    return {
        'data': json.loads(campus.to_json()),
        'updated': True,
        'error': None
    }

# deletes a campus
def adminDeleteCampus(campusid):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    # check if the campus exist in the database
    campus = Campuses.objects(id=campusid)
    if (campus == None): return ErrorGen.invalidRequestError(error='NonexistentCampus')

    campus.delete()
    return {
        'data': json.loads(campus.to_json()),
        'deleted': True,
        'error': None
    }

# archives all the latest opcr
def adminArchiveAllOPCR():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    # retrieve all the opcr that are unarchive and archive it
    unarchivedOPCR = OPCR.objects(archived=False)
    for opcr in unarchivedOPCR:
        opcr.update(archived=True)

    return {
        'data': None,
        'archived': True,
        'error': None
    }