'''
    This file will contain the routes and their specific procedures,
    when complex (ofc, not the basic ones) procedures are need to
    be added such as CRUD with complex computation, summarization, etc.
    these part will be added on modules folder.

    Also, please sort the functions below by its function name.

    Happy coding :>
    - Hubert
'''
from flask import jsonify, request
from app import app
from app.database.models import Accounts

@app.route("/")
def root():
    return jsonify({
        'message': 'Welcome to PCR-API, this is the flask implementation of the previous system (OPCR) and is expanded its functionality for office head, individuals, and pmt.',
        'api_routes': {
            '/': 'contains the welcome message'
        }
    })

# returns all the account info from the database
# excluding the password
@app.route('/admin/account')
def adminAccount():
    accounts = Accounts.objects().to_json()
    data = {
        'data': accounts,
        'error': None
    }
    return jsonify(data)
    # return jsonify({
    #     'data': [{
    #         '_id': '0aec3b21ea123',
    #         'username': 'juandelacruz',
    #         'permission': 'head'
    #     }],
    #     'error': None
    # })

# returns the account info from the database where user
# having the spcified id
@app.route('/admin/account/<id>')
def adminAccountWithID(id):
    account = Accounts.objects(id=id).first().to_json()
    data = {
        'data': account,
        'error': None
    }
    return data
    # return jsonify({
    #     'data': {
    #         '_id': '0aec3b21ea123',
    #         'username': 'juandelacruz',
    #         'permission': 'head'
    #     },
    #     'error': None
    # })

# creates a new account for PMT
@app.route('/admin/account/create/pmt', methods=['POST'])
def adminCreateAccountPMT():
    accountDetails = request.get_json(force=True)    
    new_account = Accounts(
        name = accountDetails['name'],
        username=accountDetails['username'],
        email=accountDetails['email'],
        password=accountDetails['password'],
        permission='pmt'
    )
    new_account.save()
    return jsonify({
        'id': str(new_account.id),
        'created': True,
        'permission': 'pmt',
        'error': None
    })

# creates a new account for office head
@app.route('/admin/account/create/head', methods=['POST'])
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
    return jsonify({
        'id': str(new_account.id),
        'created': True,
        'permission': 'head',
        'error': None
    })


# creates a new account for office individuals
@app.route('/admin/account/create/indiv', methods=['POST'])
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
    return jsonify({
        'id': str(new_account.id),
        'created': True,
        'permission': 'indv',
        'error': None
    })
