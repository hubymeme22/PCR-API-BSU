from flask import request
from app.database.models import Accounts, Campuses
from app.modules import ErrorGen, Sessions
from bson.objectid import ObjectId
import json

# encapsulated token checking for admin part
def adminTokenCheck(token: str=None):
    return None
    if (token == None):
        return ErrorGen.invalidRequestError(
            error='NoCookie',
            statusCode=403)

    sessinfo = Sessions.getSessionInfo(token)
    if (sessinfo == None):
        return ErrorGen.invalidRequestError(
            error='ExpiredCookie',
            statusCode=403)

    if (sessinfo['permission'] != 'admin'):
        return ErrorGen.invalidRequestError(
            error='InvalidPermission',
            statusCode=403)

# returns all the account info from the database
# excluding the password
def adminAccount():
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
    if (tokenStatus != None): return tokenStatus

    accounts = Accounts.objects().to_json()
    return {
        'data': json.loads(accounts),
        'error': None
    }

# returns the account info from the database where user
# having the spcified id
def adminAccountWithID(id):
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
    if (tokenStatus != None): return tokenStatus

    account = Accounts.objects(id=id).first().to_json()
    return {
        'data': json.loads(account),
        'error': None
    }

# creates a new account for PMT
def adminCreateAccountPMT():
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
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
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
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
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
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
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
    if (tokenStatus != None): return tokenStatus

    campusDetails: dict = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'offices'],
        jsonRequest=campusDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

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
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
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
    otherCampuses = Campuses.objects(name=campusDetails['campus']).first()
    if (otherCampuses == None):
        return ErrorGen.invalidRequestError(error='NonexistentCampus', statusCode=403)

    otherCampuses.pmt.append(campusDetails['pmtid'])
    otherCampuses.save()

    return {
        'data': json.loads(otherCampuses.to_json()),
        'error': None
    }

# retrieves all the campuses
def adminGetCampuses():
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
    if (tokenStatus != None): return tokenStatus

    campuses = Campuses.objects()
    return {
        'data': json.loads(campuses.to_json()),
        'error': None
    }

# deletes office data and remove the office head access
def adminDeleteOffice(campusid, departmentid):
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
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
    tokenStatus = adminTokenCheck(request.cookies.get('token'))
    if (tokenStatus != None): return tokenStatus

    # check if the campus exist in the database
    campus = Campuses.objects(id=campusid).first()
    if (campus == None): ErrorGen.invalidRequestError(error='NonexistentCampus')

    # retrieve and check parameters
    campusData = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(['name', 'offices'], campusData)
    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    # check every office parameters
    for officeData in campusData['offices']:
        missedOfficeParam = ErrorGen.parameterCheck(['name', 'head', 'opcr'], officeData)
        if (len(missedOfficeParam) > 0):
            return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    # if existing opcr is passed alongside with old opcr
    # convert the id into valid id format
    for i in len(campusData['offices']):
        officeData = campusData['offices'][i]
        if ('_id' in officeData):
            campusData['offices'][i]['_id'] = ObjectId(officeData['_id']['$oid'])

    # campuses update
    campus.update(name=campusData['name'], offices=campusData['offices'])
    return {
        'data': None,
        'updated': True,
        'error': None
    }