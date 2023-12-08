from app.database.dbConnection import AccountDBFunctionalities, AdminFunctionalities, CampusesFunctionalities
from app.modules import ErrorGen, Sessions
from app.module_v2 import Utils
from flask import request

#########################
#  Parameter checkers   #
#########################
def createAccountParamCheck():
    userAccount = request.get_json(force=True)
    missingParams = ErrorGen.parameterCheck(['name', 'username', 'email', 'password'], userAccount)

    if (len(missingParams) > 0):
        return ErrorGen.invalidRequestError(
            error=f'MissingParams={missingParams}')

def createCampusParamCheck():
    campusData = request.get_json(force=True)
    missingParams = ErrorGen.parameterCheck(['name', 'offices'], campusData)

    if (len(missingParams) > 0):
        return ErrorGen.invalidRequestError(
            error=f'MissingParams={missingParams}')

    for office in campusData['offices']:
        missingParams = ErrorGen.parameterCheck(['name'], office)
        if (len(missingParams) > 0):
            return ErrorGen.invalidRequestError(
                error=f'MissingParams=[offices]{missingParams}')

def assignPmtParamCheck():
    requestData = request.get_json(force=True)
    missingParams = ErrorGen.parameterCheck(['campusid', 'pmtid'], requestData)

    if (len(missingParams) > 0):
        return ErrorGen.invalidRequestError(
            error=f'MissingParams={missingParams}')

def assignHeadParamCheck():
    requestData = request.get_json(force=True)
    missingParams = ErrorGen.parameterCheck(['campusid', 'departmentid', 'headid'], requestData)

    if (len(missingParams) > 0):
        return ErrorGen.invalidRequestError(
            error=f'MissingParams={missingParams}')

#################################
#  Route logic implementations  #
#################################
def assignPmtToCampus():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None):
        return tokenStatus

    requestData = request.get_json(force=True)
    try:
        assigning = AdminFunctionalities.assignPmtToCampus(requestData['pmtid'], requestData['campusid'])
        if (assigning.acknowledged): return {'updated': True, 'error': None}
        raise Exception('Mongoerror')

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def assignHeadToDepartment():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None):
        return tokenStatus

    requestData = request.get_json(force=True)
    try:
        assigning = AdminFunctionalities.assignHeadToDepartment(requestData['headid'], requestData['campusid'], requestData['departmentid'])
        if (assigning.acknowledged): return {'updated': True, 'error': None}
        raise Exception('Mongoerror')

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def createAccount(type: str):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None):
        return tokenStatus

    accountDetails = request.get_json(force=True)
    accountDetails.update({'permission': type})
    try:
        createResponse = AccountDBFunctionalities.createAccount(accountDetails)
        if (createResponse.acknowledged): return {'created': True, 'error': None}
        raise Exception('MongoError')

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def createCampus():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    campusData = request.get_json(force=True)
    campusData.update({'pmt': []})

    for oi in range(len(campusData['offices'])):
        campusData['offices'][oi].update({
            'head': None,
            'opcr': []
        })

    try:
        createdCampus = CampusesFunctionalities.createNewCampus(campusData)
        if (createdCampus.acknowledged):
            return {'created': True, 'error': None}
        raise Exception('MongoError')
    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def deleteCampusByID(campusid: str):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None): return tokenStatus

    try:
        campusData = CampusesFunctionalities.getCampusDetails(campusid)
        if (campusData == None):
            return ErrorGen.invalidRequestError(
                error='NonexistentCampus',
                statusCode=404)

        deleteCampusData = CampusesFunctionalities.deleteCampusByID(campusid)
        if (deleteCampusData.acknowledged):
            return {'deleted': True, 'error': None}
        raise Exception('MongoError')
    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def getAllAccounts():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None):
        return tokenStatus

    try:
        accountList = AccountDBFunctionalities.getAllAccounts()
        accountList = [Utils.convertToLegacy(account) for account in accountList]
        return {'data': accountList, 'error': None}

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def getAllCampuses():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None):
        return tokenStatus

    try:
        campusList = CampusesFunctionalities.getAllCampuses()
        campusList = [Utils.convertToLegacy(campus) for campus in campusList]

        # convert the office ids to legace id format
        for ci, campus in enumerate(campusList):
            for oi, office in enumerate(campus['offices']):
                campusList[ci]['offices'][oi] = Utils.convertToLegacy(office)
                campusList[ci]['offices'][oi] = Utils.convertLegacyToString(campusList[ci]['offices'][oi], 'head')
                campusList[ci]['offices'][oi]['opcr'] = [opcr.__str__() for opcr in campusList[ci]['offices'][oi]['opcr']]
            for pi, pmt in enumerate(campus['pmt']):
                campusList[ci]['pmt'][pi] = pmt.__str__()

        return {'data': campusList, 'error': None}

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def getAllHeadAccounts():
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None):
        return tokenStatus

    try:
        accountList = AccountDBFunctionalities.getAccountsByPermission('head')
        accountList = [Utils.convertToLegacy(account) for account in accountList]
        return {'data': accountList, 'error': None}


    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)

def getDepartmentByCampusID(campusid: str):
    tokenStatus = Sessions.requestTokenCheck('admin')
    if (tokenStatus != None):
        return tokenStatus

    try:
        campusDetails = CampusesFunctionalities.getCampusDetails(campusid)
        if (campusDetails == None):
            return ErrorGen.invalidRequestError(
                error='NonexistentCampus',
                statusCode=404)

        campusOffice = campusDetails['offices']
        officesData = []
        for office in campusOffice:
            parsedOffice = Utils.convertToLegacy(office)
            parsedOffice = Utils.convertLegacyToString(parsedOffice, 'head')
            officesData.append(parsedOffice)

        return {'data': officesData, 'error': None}

    except Exception as e:
        return ErrorGen.invalidRequestError(
            error=str(e),
            statusCode=500)