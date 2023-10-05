'''
    This file will contain the routes and their specific procedures,
    when complex (ofc, not the basic ones) procedures are need to
    be added such as CRUD with complex computation, summarization, etc.
    these part will be added on modules folder.

    Also, please sort the functions below by its function name.

    Happy coding :>
    - Hubert
'''
from flask import request
from app import app
from app.database.models import Accounts, Targets, Offices
import json

@app.route("/")
def root():
    return {
        'message': 'Welcome to PCR-API, this is the flask implementation of the previous system (OPCR) and is expanded its functionality for office head, individuals, and pmt.',
        'api_routes': {
            '/': 'contains the welcome message'
        }
    }

# returns all the account info from the database
# excluding the password
@app.route('/admin/account')
def adminAccount():
    accounts = Accounts.objects().to_json()
    data = {
        'data': accounts,
        'error': None
    }
    return data
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
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'pmt',
        'error': None
    }

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
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'head',
        'error': None
    }


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
    return {
        'id': str(new_account.id),
        'created': True,
        'permission': 'indv',
        'error': None
    }


# create new target record (sample route only for testing purposes)
@app.route('/create/target', methods = ["POST"])
def create_target():
    data = request.get_json(force=True)
    # data = {
    #     "name": "some name",
    #     "success": [
    #         {
    #             "indicator": "Indicator 1",
    #             "budget": 1000.5,
    #             "division": "division 1",
    #             "accomplishment": "accomplishment 1",
    #             "rating": [1, 0, 1, 0, 0],
    #             "remarks": ["comment 1", "comment 2", "comment 3"],
    #             "assigned_to": ["01a", "01b", "01c"]
    #         },
    #         {
    #             "indicator": "Indicator 2",
    #             "budget": 2000.5,
    #             "division": "division 2",
    #             "accomplishment": "accomplishment 2",
    #             "rating": [1, 0, 1, 0, 0],
    #             "remarks": ["comment 1", "comment 2", "comment 3"],
    #             "assigned_to": ["01a", "01b", "01c"]
    #         }
    #     ]
    # }

    target = Targets(**data)
    target.save()

    return {
        'message': "New Target created",
        "id": str(target.id)
    }

# read the target in db based on name attribute (sample route only for testing purposes)
@app.route('/get/target/<name>', methods = ['GET'])
def get_target(name):
    target = Targets.objects(name=name).first()
    if target:
        result = target.to_json()
        return json.loads(result)    
    return {'message': 'target not found'}


# create office record (sample route only for testing purposes)
@app.route('/create/office', methods = ["POST"])
def create_office():
    data = request.get_json(force=True)
    office = Offices(**data)
    office.save()
    return {
        'message': "Office created",
        'id': str(office.id)
    }

# read office in db based on name attribute (sample route only for testing purposes)
@app.route('/get/office/<name>', methods = ['GET'])
def get_office(name):
    office = Offices.objects(name=name).first()
    if office:
        return json.loads(office.to_json())
    return {'message': 'office not found'}

    