from flask import request
from app.database.models import Accounts
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