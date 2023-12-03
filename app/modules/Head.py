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
        latestOPCR = OPCR.objects(owner=userSessionInfo['userid'], archived=False).first()

        if (latestOPCR == None):
            newOpcr = OPCR(targets=[opcr], owner=userSessionInfo['userid'])
            newOpcr.save()
            return { 'added': True, 'data': None, 'error': None }

        # format the target before appending new value
        convertedTargets = []
        parsedOPCR = json.loads(latestOPCR.to_json())
        for target in parsedOPCR['targets']:
            target.update({'_id': ObjectId(target['_id']['$oid'])})

            for sidx in range(len(target['success'])):
                target['success'][sidx]['_id'] = ObjectId(target['success'][sidx]['_id']['$oid'])
            convertedTargets.append(target)


        # add a new target
        convertedTargets.append(opcr)
        latestOPCR.update(targets=convertedTargets)
        return { 'added': True, 'data': None, 'error': None }

    except Exception as e:
        return ErrorGen.invalidRequestError(error=str(e), statusCode=500)

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
    newTargetValue = []
    for target in userOpcrParsed['targets']:
        target.update({'_id': ObjectId(target['_id']['$oid'])})
        for successIndex, success in enumerate(target['success']):
            target['success'][successIndex].update({ '_id': ObjectId(success['_id']['$oid']) })
        newTargetValue.append(target)

    newTargetValue += targetList
    userOPCR.update(targets=newTargetValue)
    return {
        'added': True,
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
        userOpcr = OPCR.objects(owner=userDetails['userid'], archived=False)

        if (userOpcr == None):
            print('Userid:', userDetails['userid'])
            print('No opcr retrieved')
            print(json.loads(OPCR.objects().to_json()))
            return {}

        return {
            'data': json.loads(userOpcr.to_json()),
            'error': None
        }

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
