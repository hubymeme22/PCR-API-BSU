from app.database.dbConnection import HeadFunctionalities, CampusesFunctionalities
from app.modules import Sessions, ErrorGen
from app.module_v2 import Utils
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
            latestOpcr = HeadFunctionalities.createMFO(userInfos['userid'], targetValues)
            campusMatch = CampusesFunctionalities.getHeadCampus(userInfos['userid'])
            if (campusMatch == None): raise Exception('OpcrOrCampusNotRegistered')

            opcrID = latestOpcr.inserted_id
            campusID = campusMatch['_id'].__str__()

            for office in campusMatch['offices']:
                officeId = office['_id'].__str__()

                if ((office.get('head') != None) and
                    (office.get('head').__str__() == userInfos['userid'])):

                    opcrRegistered = CampusesFunctionalities.addDepartmentOpcr(campusID, officeId, opcrID)
                    if (opcrRegistered.acknowledged):
                        return {'created': True, 'error': None}

            raise Exception('MongoError')
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

def deleteMFOById(mfoid: str):
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None):
        return tokenStatus

    try:
        userInfos = Sessions.getSessionInfo(request.headers.get('Authorization'))
        deleted = HeadFunctionalities.deleteMFO(userInfos['userid'], mfoid)
        if (deleted.acknowledged):
            return {'deleted': True, 'error': None}
        raise Exception('MongoError')

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def updateMFO(mfoid: str):
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None):
        return tokenStatus

    userInfos = Sessions.getSessionInfo(request.headers.get('Authorization'))
    targetValues = request.get_json(force=True)

    try:
        updated = HeadFunctionalities.updateMFO(userInfos['userid'], mfoid, targetValues)
        if (updated == None): return ErrorGen.invalidRequestError(
            error='InvalidID',
            statusCode=418)

        return {
            'updated': True,
            'data': {},
            'error': None
        }

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def getLatestOpcr():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None):
        return tokenStatus

    userInfos = Sessions.getSessionInfo(request.headers.get('Authorization'))
    latestOpcr = HeadFunctionalities.getOpcrData(userInfos['userid'])
    if (latestOpcr == None):
        return {'data': [], 'error': None}

    for it, target in enumerate(latestOpcr['targets']):
        latestOpcr['targets'][it] = Utils.convertToLegacy(target)
        for ins, success in enumerate(target['success']):
            latestOpcr['targets'][it]['success'][ins]  = Utils.convertLegacyToString(success, 'oid')

    return {
        'data': latestOpcr['targets'],
        'error': None
    }