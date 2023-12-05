from app.database.dbConnection import CampusesFunctionalities, HeadFunctionalities, OPCRFunctionalities
from app.modules import Sessions, ErrorGen
from flask import request

#########################
#  Parameter checkers   #
#########################
def checkAddMfoParams():
    userOpcr = request.get_json(force=True)
    missingParams = ErrorGen.parameterCheck(['name', 'success'], userOpcr)

    if (len(missingParams) > 0):
        return ErrorGen.invalidRequestError(
            error=f'MissingParams={missingParams}')

    for success in userOpcr['success']:
        missingParams = ErrorGen.parameterCheck(
            requiredParams=['accomplishment', 'assigned_to', 'budget', 'division', 'indicator', 'rating', 'remarks'],
            jsonRequest=success)
        if (len(missingParams) > 0):
            return ErrorGen.invalidRequestError(
            error=f'MissingParams={missingParams}')


#################################
#  Route logic implementations  # 
#################################
def addMFO():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None):
        return tokenStatus

    userInfos = Sessions.getSessionInfo(request.headers.get('Authorization'))
    userOpcr = HeadFunctionalities.getOpcrData(userInfos['userid'])
    targetValues = request.get_json(force=True)

    try:
        if (userOpcr == None):
            HeadFunctionalities.createMFO(userInfos['userid'], targetValues)
            return {
                'updated': True,
                'data': None,
                'error': None
            }

        HeadFunctionalities.appendNewMFO(userOpcr['_id'], targetValues)
        return {
            'updated': True,
            'data': None,
            'error': None
        }

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)