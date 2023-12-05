from flask import request
from bson.objectid import ObjectId
from app.database.models import OPCR, Accounts, Campuses
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
            if ('_id' in opcr): del opcr['_id']
            savedOpcr = OPCR(targets=[opcr], owner=userSessionInfo['userid']).save()
            campusAssigned = json.loads(Campuses.objects().to_json())

            # append the opcr id to the office-pmt
            officeFound = False
            for campus in campusAssigned:
                if (officeFound): break
                for oid, office in enumerate(campus['offices']):
                    if (office['head'] == userSessionInfo['userid']):
                        campus['offices'][oid]['opcr'].append(savedOpcr.id)
                        officeFound = True
                        break

            return { 'added': True, 'data': None, 'error': None }

        # format the target before appending new value
        updateFlagSet = False
        updatedCount  = 0
        convertedTargets = []
        targetOpcrID = opcr['_id']['$oid']
        parsedOPCR = json.loads(latestOPCR.to_json())

        for target in parsedOPCR['targets']:
            updateFlagSet = (target['_id']['$oid'] == targetOpcrID)
            updatedCount += updateFlagSet

            target.update({'_id': ObjectId(target['_id']['$oid'])})
            if (updateFlagSet): target.update({'name': opcr['name']})

            for sidx, success in enumerate(target['success']):
                dbsuccessid = success['_id']['$oid']
                target['success'][sidx].update({'_id': ObjectId(dbsuccessid)})

                # also update values if there's a matched id
                if (updateFlagSet):
                    for successpayload in opcr['success']:
                        if (successpayload['_id']['$oid'] == dbsuccessid):
                            target['success'][sidx].update({
                                'indicator': successpayload['indicator'],
                                'budget': successpayload['budget'],
                                'division': successpayload['division'],
                                'accomplishment': successpayload['accomplishment'],
                                'rating': successpayload['rating'],
                                'remarks': successpayload['remarks'],
                                'assigned_to': successpayload['assigned_to']
                            })

            updateFlagSet = False
            convertedTargets.append(target)

        # update-only operation
        if (updatedCount > 0):
            latestOPCR.update(targets=convertedTargets)
            return { 'added': True, 'data': None, 'error': None }

        # new ocpr added operation
        del opcr['_id']
        for sid, success in enumerate(opcr['success']):
            del opcr['success'][sid]['_id']

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
    userOpcrTarget = userOpcrParsed['targets']
    updateCount = 0

    for dbti, dbtarget in enumerate(userOpcrTarget):
        dbtargetid = dbtarget['_id']['$oid']
        userOpcrTarget[dbti]['_id'] = ObjectId(dbtargetid)

        toBeEditedOpcr = False
        for localtarget in targetList:
            if (localtarget['_id']['$oid'] == dbtargetid):
                toBeEditedOpcr = True
                updateCount += 1
                break

        if (toBeEditedOpcr):
            userOpcrTarget[dbti].update({'name': localtarget['name']})

        for dbsi, dbsuccess in enumerate(dbtarget['success']):
            dbsuccessid = dbsuccess['_id']['$oid']
            userOpcrTarget[dbti]['success'][dbsi]['_id'] = ObjectId(dbsuccessid)

            if (toBeEditedOpcr):
                for localsuccess in localtarget['success']:
                    if (localsuccess['_id']['$oid'] == dbsuccessid):
                        userOpcrTarget[dbti]['success'][dbsi].update({
                                'indicator': localsuccess['indicator'],
                                'budget': localsuccess['budget'],
                                'division': localsuccess['division'],
                                'accomplishment': localsuccess['accomplishment'],
                                'rating': localsuccess['rating'],
                                'remarks': localsuccess['remarks'],
                                'assigned_to': localsuccess['assigned_to']
                        })

        toBeEditedOpcr = False

    if (updateCount == 0):
        userOPCR.update(targets=targetList)
        return {
            'added': True,
            'data': None,
            'error': None
        }

    userOPCR.update(targets=userOpcrTarget)
    return {
        'added': True,
        'data': { 'updates': updateCount },
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
        userOpcr = OPCR.objects(owner=userDetails['userid'], archived=False).first()

        if (userOpcr == None):
            print('Userid:', userDetails['userid'])
            print('No opcr retrieved')
            print(json.loads(OPCR.objects().to_json()))
            return {}

        opcrParsed = json.loads(userOpcr.to_json())
        return {
            'data': opcrParsed['targets'],
            'error': None
        }

    except Exception as e:
        print(e)
        return ErrorGen.invalidRequestError(statusCode=500)

# retrieves the opcr specified
def retrieveSingleOPCR(id):
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails = Sessions.getSessionInfo(usertoken)
        userOpcr = OPCR.objects(owner=userDetails['userid'], archived=False).first()

        if (userOpcr == None): return {
            'data': {},
            'error': None
        }

        userOpcr = json.loads(userOpcr.to_json())
        for target in userOpcr['targets']:
            print(target['_id'])
            if (target['_id']['$oid'] == id):
                return {
                    'data': target,
                    'error': None
                }
        return ErrorGen.invalidRequestError(error='NonexistentTargetID', statusCode=404)

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

# submits the opcr to pmt and mark as in progess
def submitOpcrToPmt():
    tokenStatus = Sessions.requestTokenCheck('head')
    if (tokenStatus != None): return tokenStatus

    usertoken: str = request.headers.get('Authorization')
    try:
        userDetails: dict = Sessions.getSessionInfo(usertoken)
        latestOpcr = OPCR.objects(owner=userDetails['userid'], archived=False).first()
        if (latestOpcr == None): return ErrorGen.invalidRequestError(error='NoOPCRAssigned', statusCode=418)

        latestOpcrParsed = json.loads(latestOpcr.to_json())
        if (latestOpcrParsed['status'] == 'calibrating'):
            return {'submited': False, 'error': 'AlreadyCalibrating'}

        if (latestOpcrParsed['status'] == 'calibrated'):
            return {'submited': False, 'error': 'AlreadyCalibrated'}

        latestOpcr.update(status='calibrating')
        return {
            'submited': True,
            'error': None
        }

    except:
        return ErrorGen.invalidRequestError(statusCode=500)