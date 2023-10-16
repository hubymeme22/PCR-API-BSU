from flask import request
from app.database.models import OPCR
from app.modules import ErrorGen, Sessions
import json

# generates a new opcr for the user
def createOPCR():
    userToken = request.cookies.get('token')
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
    usertoken: str = request.cookies.get('token')

    try:
        userDetails: dict = Sessions.getSessionInfo(usertoken)
        userOpcr = OPCR.objects(owner=userDetails['userid'])
        userOpcrParsed = [json.loads(OPCRObject.to_json()) for OPCRObject in userOpcr]
        return { 'data': userOpcrParsed, 'error': None }

    except:
        return ErrorGen.invalidRequestError(statusCode=500)