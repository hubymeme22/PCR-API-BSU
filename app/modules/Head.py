from flask import request
from bson.objectid import ObjectId
from app.database.models import OPCR, Accounts
from app.modules import ErrorGen, Sessions
import json

# generates a new opcr for the user
def addMFO():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    userToken = request.headers.get('Authorization')
    opcr = request.get_json(force=True)

    # check each parameters in request
    missingArgs = ErrorGen.parameterCheck(
        requiredParams=['name', 'success'],
        jsonRequest=opcr)

    if (len(missingArgs)):
        return ErrorGen.invalidRequestError(error=f'MissingParams={missingArgs}')

    for success in opcr['success']:
        missingArgs = ErrorGen.parameterCheck(
            requiredParams=['indicator', 'budget', 'division', 'accomplishment', 'rating', 'assigned_to'],
            jsonRequest=success)

        if (len(missingArgs)):
            return ErrorGen.invalidRequestError(error=f'MissingParams={missingArgs}')

    # retrieve user info based on session
    try:
        userSessionInfo = Sessions.getSessionInfo(userToken)
        latestOPCR = OPCR.objects().first()

        if (latestOPCR == None):
            newOpcr = OPCR(targets=[opcr], owner=userSessionInfo['userid'])
            newOpcr.save()
            return { 'added': True, 'data': None, 'error': None }

        # format the target before appending new value
        convertedTargets = []
        for target in latestOPCR['targets']:
            target.update({'_id': ObjectId(target['_id']['$oid'])})
            convertedTargets.append(target)

        # add a new target
        convertedTargets.append(opcr)
        latestOPCR.update(target=convertedTargets)
        return { 'added': True, 'data': None, 'error': None }

    except Exception as e:
        return ErrorGen.invalidRequestError(error=str(e), statusCode=500)

def createOPCR(opcrid):
    return {}

# retrieves specific opcr of the user
def retrieveUserOPCR():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails = Sessions.getSessionInfo(usertoken)
        userOpcr = OPCR.objects(owner=userDetails['userid']).first()
        if (userOpcr == None): return {}
        return {
            'data': json.loads(userOpcr),
            'error': None
        }

    except Exception as e:
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
