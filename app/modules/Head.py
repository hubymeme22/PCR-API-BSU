from flask import request
from app.database.models import OPCR
from app.modules import ErrorGen, Sessions

# generates a new opcr for the user
def createOPCR():
    userToken = request.cookies.get('token')
    opcrDetails: dict = request.get_json(force=True)

    # checks for missing required parameters in targets
    missingParams = ErrorGen.parameterCheck(
        requiredParams=opcrDetails.get('targets'),
        jsonRequest=opcrDetails)

    if (len(missingParams) > 0):
        return ErrorGen.invalidRequestError(
            datavalue='',
            error=f'MissingParams={missingParams}')

    # get session details and check the token status
    userDetails = Sessions.getSessionInfo(userToken)
    if ((userToken == None) and (userDetails == None)):
        return {
            'created': False,
            'error': 'InvalidPermission'
        }

    # set the user's id as the owner of the new OPCR
    opcrDetails.update({'owner': userDetails['userid']})
    newUserOPCR = OPCR(**opcrDetails)
    newUserOPCR.save()

    return {
        'created': True,
        'error': None
    }
