from flask import request
from app.database.models import OPCR, Accounts
from app.modules import ErrorGen, Sessions
from app.modules.Sessions import getSessionInfo
import json

# generates a new opcr for the user
def createOPCR():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    userToken = request.headers.get('Authorization')
    opcrDetails: list = request.get_json(force=True)

    # check each parameters in request
    for opcr in opcrDetails:
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
        newOpcr = OPCR(targets=opcrDetails, owner=userSessionInfo['userid'])
        newOpcr.save()

        return { 'created': True, 'error': None }

    except:
        return ErrorGen.invalidRequestError(statusCode=500)


# retrieves specific opcr of the user
def retrieveUserOPCR():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails = getSessionInfo(usertoken)
        userOpcr = OPCR.objects(owner=userDetails['userid'])
        userOpcrParsed = [json.loads(OPCRObject.to_json()) for OPCRObject in userOpcr]
        return { 'data': userOpcrParsed, 'error': None }

    except Exception as e:
        return ErrorGen.invalidRequestError(statusCode=500)

# retrieves all the users under this head account
def retrieveIndividuals():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails: dict = getSessionInfo(usertoken)
        individualAccounts = Accounts.objects(permission='individual', superior=userDetails.get('userid')).to_json()
        responseFormat = [{'_id': {'$oid': individual['id']['$oid']}, 'name': individual['name']} for individual in individualAccounts]
        return {
            'data': responseFormat,
            'error': None
        }

    except:
        return ErrorGen.invalidRequestError(statusCode=500)
