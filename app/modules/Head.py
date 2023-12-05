from flask import request
from bson.objectid import ObjectId
from app.database.models import OPCR, Accounts, Campuses
from app.modules import ErrorGen, Sessions
import json

# generates a new opcr for the user
def addBulkMFO():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    userToken = request.headers.get('Authorization')
    targetList = request.get_json(force=True)

    for target in targetList:
        missingArgs = ErrorGen.parameterCheck(['name', 'success'], target)
        if (len(missingArgs) > 0): return ErrorGen.invalidRequestError(error=f'MissingParams={missingArgs}')

        for success in target['success']:
            missingArgs = ErrorGen.parameterCheck(['indicator', 'budget', 'division', 'accomplishment', 'rating', 'assigned_to'], success)
            if (len(missingArgs) > 0): return ErrorGen.invalidRequestError(error=f'MissingParams=success->{missingArgs}')

    userDetails = Sessions.getSessionInfo(userToken)
    userOPCR = OPCR.objects(owner=userDetails['userid'], archived=False).first()
    if (userOPCR == None):
        newOpcr = OPCR(targets=targetList, owner=userToken['userid'])
        newOpcr.save()
        return {
            'added': True,
            'error': None
        }

    # update the object id values for target and child
    userOpcrParsed = json.loads(userOPCR.to_json())
    userOpcrTarget = userOpcrParsed['targets']
    updateCount = 0

    for dbti, dbtarget in enumerate(userOpcrTarget):
        dbtargetid = dbtarget['_id']['$oid']
        userOpcrTarget[dbti]['_id'] = ObjectId(dbtargetid)

        toBeEditedOpcr = False
        for localtarget in targetList:
            if (localtarget['_id']['$oid'] == dbtargetid):
                toBeEditedOpcr = True
                updateCount += 1
                break

        if (toBeEditedOpcr):
            userOpcrTarget[dbti].update({'name': localtarget['name']})

        for dbsi, dbsuccess in enumerate(dbtarget['success']):
            dbsuccessid = dbsuccess['_id']['$oid']
            userOpcrTarget[dbti]['success'][dbsi]['_id'] = ObjectId(dbsuccessid)

            if (toBeEditedOpcr):
                for localsuccess in localtarget['success']:
                    if (localsuccess['_id']['$oid'] == dbsuccessid):
                        userOpcrTarget[dbti]['success'][dbsi].update({
                                'indicator': localsuccess['indicator'],
                                'budget': localsuccess['budget'],
                                'division': localsuccess['division'],
                                'accomplishment': localsuccess['accomplishment'],
                                'rating': localsuccess['rating'],
                                'remarks': localsuccess['remarks'],
                                'assigned_to': localsuccess['assigned_to']
                        })

        toBeEditedOpcr = False

    if (updateCount == 0):
        userOPCR.update(targets=targetList)
        return {
            'added': True,
            'data': None,
            'error': None
        }

    userOPCR.update(targets=userOpcrTarget)
    return {
        'added': True,
        'data': { 'updates': updateCount },
        'error': None
    }

def createOPCR(opcrid):
    # implement soon
    return {}

# retrieves specific opcr of the user
def retrieveUserOPCR():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails = Sessions.getSessionInfo(usertoken)
        userOpcr = OPCR.objects(owner=userDetails['userid'], archived=False).first()

        if (userOpcr == None):
            return {}

        opcrParsed = json.loads(userOpcr.to_json())
        return {
            'data': opcrParsed['targets'],
            'status': opcrParsed['status'],
            'error': None
        }

    except Exception as e:
        return ErrorGen.invalidRequestError(statusCode=500)

# retrieves the opcr specified
def retrieveSingleOPCR(id):
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails = Sessions.getSessionInfo(usertoken)
        userOpcr = OPCR.objects(owner=userDetails['userid'], archived=False).first()

        if (userOpcr == None): return {
            'data': {},
            'error': None
        }

        userOpcr = json.loads(userOpcr.to_json())
        for target in userOpcr['targets']:
            print(target['_id'])
            if (target['_id']['$oid'] == id):
                return {
                    'data': target,
                    'error': None
                }
        return ErrorGen.invalidRequestError(error='NonexistentTargetID', statusCode=404)

    except Exception:
        return ErrorGen.invalidRequestError(statusCode=500)

# retrieves all the users under this head account
def retrieveIndividuals():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails: dict = Sessions.getSessionInfo(usertoken)
        individualAccounts = json.loads(Accounts.objects(permission='individual', superior=userDetails.get('userid')).to_json())
        responseFormat = [{'_id': {'$oid': individual['_id']['$oid']}, 'name': individual['name']} for individual in individualAccounts]
        return {
            'data': responseFormat,
            'error': None
        }
    except:
        return ErrorGen.invalidRequestError(statusCode=500)

# submits the opcr to pmt and mark as in progess
def submitOpcrToPmt():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails: dict = Sessions.getSessionInfo(usertoken)
        latestOpcr = OPCR.objects(owner=userDetails['userid'], archived=False).first()
        if (latestOpcr == None): return ErrorGen.invalidRequestError(error='NoOPCRAssigned', statusCode=418)

        latestOpcrParsed = json.loads(latestOpcr.to_json())
        if (latestOpcrParsed['status'] == 'calibrating'):
            return {'submited': False, 'error': 'AlreadyCalibrating'}

        if (latestOpcrParsed['status'] == 'calibrated'):
            return {'submited': False, 'error': 'AlreadyCalibrated'}

        latestOpcr.update(status='calibrating')
        return {
            'submited': True,
            'error': None
        }

    except:
        return ErrorGen.invalidRequestError(statusCode=500)