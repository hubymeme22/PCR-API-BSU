from app.database.dbConnection import PMTFunctionalities
from app.modules import Sessions
from flask import request

def getOpcrReport():
    tokenStatus = Sessions.requestTokenCheck('pmt')
    if (tokenStatus != None):
        return tokenStatus

    userInfos = Sessions.getSessionInfo(request.headers.get('Authorization'))
    userOpcr = PMTFunctionalities.getOpcrData(userInfos['userid'])
    userOpcr = [opcr for opcr in userOpcr]

    return {
        'data': userOpcr,
        'error': None
    }