from flask import request
from app.database.models import Accounts, Campuses
from app.modules import ErrorGen
import json

# returns all the account info from the database
# excluding the password
def adminAccount():
    accounts = Accounts.objects().to_json()
    return {
        'data': json.loads(accounts),
        'error': None
    }

# returns the account info from the database where user
# having the spcified id
def adminAccountWithID(id):
    account = Accounts.objects(id=id).first().to_json()
    return {
        'data': json.loads(account),
        'error': None
    }

# creates a new account for PMT
def adminCreateAccountPMT():
    accountDetails = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'username', 'email', 'password'],
        jsonRequest=accountDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    new_account = Accounts(
        name = accountDetails['name'],
        username=accountDetails['username'],
        email=accountDetails['email'],
        password=accountDetails['password'],
        superior = accountDetails.get('superior'),
        permission='pmt'
    )

    new_account.save()
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'pmt',
        'error': None
    }

# creates a new account for office head
def adminCreateAccountHead():
    accountDetails = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'username', 'email', 'password'],
        jsonRequest=accountDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    new_account = Accounts(
        name = accountDetails['name'],
        username=accountDetails['username'],
        email=accountDetails['email'],
        password=accountDetails['password'],
        permission='head'
    )
    new_account.save()
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'head',
        'error': None
    }


# creates a new account for office individuals
def adminCreateAccountIndiv():
    accountDetails = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'username', 'email', 'password', 'superior'],
        jsonRequest=accountDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    new_account = Accounts(
        name = accountDetails['name'],
        username=accountDetails['username'],
        email=accountDetails['email'],
        password=accountDetails['password'],
        permission='individual'
    )
    new_account.save()
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'indv',
        'error': None
    }

# creates and registers new campus
def adminCreateCampus():
    campusDetails: dict = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['name', 'offices'],
        jsonRequest=campusDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    # initialize the list of pmt ids as empty
    campusDetails.update({'pmt': []})
    newCampus = Campuses(**campusDetails)
    newCampus.save()

    return {
        'id': str(newCampus.id),
        'created': True,
        'error': None
    }

# assigns the pmt to a specific campus
def adminAssignPmtCampus():
    campusDetails = request.get_json(force=True)
    missedParams = ErrorGen.parameterCheck(
        requiredParams=['campus', 'pmtid'],
        jsonRequest=campusDetails)

    if (len(missedParams) > 0):
        return ErrorGen.invalidRequestError(error=f'MissedParams={missedParams}')

    # checks if the pmt has already campus assigned
    otherCampuses = Campuses.objects(pmt__in=campusDetails['pmtid']).first()
    if (otherCampuses != None):
        return ErrorGen.invalidRequestError(error='CampusAlreadyAssigned', statusCode=403)

    # assign the pmt to campus
    otherCampuses = Campuses.objects(name=campusDetails['campus']).first()
    if (otherCampuses == None):
        return ErrorGen.invalidRequestError(error='NonexistentCampus', statusCode=403)

    otherCampuses.pmt.append(campusDetails['pmtid'])
    otherCampuses.save()

    return {
        'data': otherCampuses.to_json(),
        'error': None
    }