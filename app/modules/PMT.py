from flask import request
from app.database.models import Campuses, OPCR, Accounts, Sessions
from app.modules import ErrorGen, Sessions
from bson import ObjectId
import json

# Get all the OPCR records
def get_opcr():
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None): return tokenStatus

    # Fetch all OPCR objects
    target = OPCR.objects()
    if target: return {
        'data': json.loads(target.to_json()),
        'error': None
    }

    return {
        'data': [],
        'error': None
    }

# Get an OPCR record based on ID
def opcr_by_id(id):
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None): return tokenStatus

    # Check validity of ID format
    if not ObjectId.is_valid(id):
        return ErrorGen.invalidRequestError(error=f"Invalid id ('{id}'). It must be a 12-byte value. See https://www.mongodb.com/docs/manual/reference/method/ObjectId/")
    
    # Fetch the OPCR object
    target = OPCR.objects(id=id).first()
    if target: return {
        'data': json.loads(target.to_json()),
        'error': None
    }

    return ErrorGen.invalidRequestError(error='NonexistentOpcrID', statusCode=404)


def opcr_by_campus():
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Get the campus(es) that the pmt is assigned into
    campuses = Campuses.objects(pmt__contains=user_info['userid']).to_json()
    
    # Get all the OPCR IDs of the campus offices
    all_opcr = []
    for campus in json.loads(campuses):
        for office in campus['offices']:
            all_opcr.extend(office['opcr'])

    # Get all the OPCR details using the OPCR IDs retreived above
    result = OPCR.objects(id__in = [ObjectId(_id) for _id in all_opcr])
    
    return {
        'data': json.loads(result.to_json())
    }, 200


# create campus record (sample route only for testing purposes)
def create_campus():
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Save data from POST request
    data = request.get_json(force=True)    
    campus = Campuses(**data)
    campus.save()
    return {
        'error': None,
        'id': str(campus.id)
    }

# read campus in db 
def get_campus():
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Fetch Campuses objects
    campuses = Campuses.objects()
    if campuses:
        return {
            'data': json.loads(campuses.to_json()),
            'error': None
        }

    return {
        'data': [],
        'error': None
    }

# read campus in db based on id attribute (sample route only for testing purposes)
def campus_by_id(id):
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Check validity of ID format
    if not ObjectId.is_valid(id):
        return ErrorGen.invalidRequestError(error=f"Invalid id ('{id}'). It must be a 12-byte value. See https://www.mongodb.com/docs/manual/reference/method/ObjectId/")
    
    # Fetch the Campus object
    campus_record = Campuses.objects(id=id).first()
    if campus_record:
        return {
            'data': json.loads(campus_record.to_json()),
            'error': None
        }

    return {
        'data': [],
        'error': None
    }


# Write remark on an OPCR object
def write_remark(id):
    # Get the OPCR object based on ID
    opcr_object = OPCR.objects(id=id).first()
    remarks = request.get_json(force = True)['remarks']

    # Place the remarks
    for i, outer_list in enumerate(remarks):
        for j, remark in enumerate(outer_list):
            opcr_object.targets[i].success[j].remarks = remark


    # Save the update
    opcr_object.save()

    return {
        'message': "Remarks written successfully"
    }

# adds a remark for specific mfo and success indicator id
def addRemarks(opcrid, mfoid):
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None): return tokenStatus

    remarkData: list = request.get_json(force=True)
    for remark in remarkData:
        missed = ErrorGen.parameterCheck(['successID', 'remarks'], remark)
        if (len(missed) > 0): return ErrorGen.invalidRequestError(error=f'MissedParams={missed}')

    latestOPCR = OPCR.objects(id=opcrid, archived=False).first()
    if (latestOPCR == None): return ErrorGen.invalidRequestError(error='NonexistentOPCR', statusCode=404)

    # retrieves the latest opcr targets and update its remarks
    parsedLatestOPCR = json.loads(latestOPCR.to_json())['targets']
    for i in range(len(parsedLatestOPCR)):
        if (mfoid == parsedLatestOPCR[i]['_id']['$oid']):
            for j in range(len(parsedLatestOPCR[i]['success'])):
                for remark in remarkData:
                    if (parsedLatestOPCR[i]['success'][j]['_id']['$oid'] == remark['successID']):
                        parsedLatestOPCR[i]['success'][j]['remarks'].append(remark['remarks'])

    # parse each object id for opcr target values
    for i in range(len(parsedLatestOPCR)):
        parsedLatestOPCR[i]['_id'] = ObjectId(parsedLatestOPCR[i]['_id']['$oid'])
        for j in range(len(parsedLatestOPCR[i]['success'])):
            parsedLatestOPCR[i]['success'][j]['_id'] = ObjectId(parsedLatestOPCR[i]['success'][j]['_id']['$oid'])

    latestOPCR.update(targets=parsedLatestOPCR)
    return {
        'data': None,
        'added': True,
        'error': None
    }

# retrieves all the offices from the campus assigned to this user
def getOfficeReport():
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None): return tokenStatus

    pmtAccountInfo = Sessions.getSessionInfo(request.headers.get('Authorization'))
    campusAssigned = json.loads(Campuses.objects().to_json())
    assigned = False

    # manually search through array
    for campus in campusAssigned:
        if (pmtAccountInfo['userid'] in campus['pmt']):
            campusAssigned = campus
            assigned = True
            break

    if (not assigned): return ErrorGen.invalidRequestError(error='UnassignedPMTAccount', statusCode=404)
    headAccounts = [(office['_id']['$oid'], office['name'], office['head']) for office in campusAssigned['offices']]
    officesOpcrReport = []

    for officeid, officeName, headID in headAccounts:
        retrievedOPCR = OPCR.objects(owner=headID, archived=False).first()
        if (retrievedOPCR == None): continue

        retrievedOPCR = json.loads(retrievedOPCR.to_json())
        officesOpcrReport.append({
            '_id': { '$oid': officeid },
            'name': officeName,
            'status': retrievedOPCR['status'],
            'progress': 50.0
        })


    return {
        'data': officesOpcrReport,
        'error': None
    }

# retrieves all the offices from the campus assigned to this user
def getOfficeOPCR():
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None): return tokenStatus

    pmtAccountInfo = Sessions.getSessionInfo(request.headers.get('Authorization'))
    campusAssigned = json.loads(Campuses.objects().to_json())
    assigned = False

    # manually search through array
    for campus in campusAssigned:
        if (pmtAccountInfo['userid'] in campus['pmt']):
            campusAssigned = campus
            assigned = True
            break

    if (not assigned): return ErrorGen.invalidRequestError(error='UnassignedPMTAccount', statusCode=404)
    headAccounts = [office['head'] for office in campusAssigned['offices']]
    officesOpcr = []

    for headID in headAccounts:
        retrievedOPCR = OPCR.objects(owner=headID, archived=False).first()
        if (retrievedOPCR == None): continue

        retrievedOPCR = json.loads(retrievedOPCR.to_json())
        officesOpcr.append(retrievedOPCR)


    return {
        'data': officesOpcr,
        'error': None
    }

# retrieves the opcr of the office
def getOpcrByOfficeID(officeid):
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None): return tokenStatus

    pmtAccountInfo = Sessions.getSessionInfo(request.headers.get('Authorization'))
    campusAssigned = Campuses.objects()

    if (len(campusAssigned) == 0):
        return ErrorGen.invalidRequestError(error='NoCampusAssigned', statusCode=500)

    campusAssigned = json.loads(campusAssigned.to_json())
    for campus in campusAssigned:
        if (pmtAccountInfo['userid'] in campus['pmt']):
            for office in campus['offices']:
                if (officeid == office['_id']['$oid']):
                    if (office['head'] == ''): return ErrorGen.invalidRequestError(
                        error='OfficeNoHeadAssigned',
                        statusCode=418)

                    latestOpcr = OPCR.objects(owner=office['head'], archived=False).first()
                    if (latestOpcr == None): return { 'data': [], 'error': None }
                    return { 'data': json.loads(latestOpcr.to_json()), 'error': None }

    return ErrorGen.invalidRequestError()