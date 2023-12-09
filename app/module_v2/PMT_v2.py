from app.database.dbConnection import PMTFunctionalities, CampusesFunctionalities, OPCRFunctionalities
from app.modules import Sessions, ErrorGen
from app.module_v2 import Utils
from flask import request

def getOpcrReport():
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None):
        return tokenStatus

    try:
        userInfos = Sessions.getSessionInfo(request.headers.get('Authorization'))
        pmtCampus = CampusesFunctionalities.getPmtCampus(userInfos['userid'])

        pmtList = []
        for office in pmtCampus['offices']:
            if (len(office['opcr']) > 0):
                opcrData = OPCRFunctionalities.getOneOpcr(office['opcr'][0].__str__())
                pmtList.append({
                    '_id': {'$oid': office['_id'].__str__()},
                    'name': office['name'],
                    'status': opcrData['status']
                })

        return {
            'data': pmtList,
            'error': None
        }

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def getOpcrByOfficeId(officeid: str):
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None):
        return tokenStatus

    try:
        opcrData = PMTFunctionalities.getOpcrDataByOfficeID(officeid)
        opcrData = Utils.convertToLegacy(opcrData)
        for it, target in enumerate(opcrData['targets']):
            updatedTarget = Utils.convertToLegacy(target)
            for si, success in enumerate(updatedTarget['success']):
                updatedTarget['success'][si] = Utils.convertLegacyToString(success, 'oid')
            opcrData['targets'][it] = updatedTarget
            opcrData['owner'] = opcrData['owner'].__str__()

        return {
            'data': opcrData,
            'error': None
        }

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)