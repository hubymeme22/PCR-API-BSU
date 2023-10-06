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
from app.database.models import Accounts, Campuses, OPCR
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
@app.route('/create/opcr', methods = ["POST"])
def create_opcr():
    data = request.get_json(force=True)
    # data = {
    #     "targets": [
    #         {
    #             "name": "some name",
    #             "success": [
    #                 {
    #                     "indicator": "Indicator 1",
    #                     "budget": 1000.5,
    #                     "division": "division 1",
    #                     "accomplishment": "accomplishment 1",
    #                     "rating": [1, 0, 1, 0, 0],
    #                     "remarks": ["comment 1", "comment 2", "comment 3"],
    #                     "assigned_to": ["01a", "01b", "01c"]
    #                 },
    #                 {
    #                     "indicator": "Indicator 2",
    #                     "budget": 2000.5,
    #                     "division": "division 2",
    #                     "accomplishment": "accomplishment 2",
    #                     "rating": [1, 0, 1, 0, 0],
    #                     "remarks": ["comment 1", "comment 2", "comment 3"],
    #                     "assigned_to": ["01a", "01b", "01c"]
    #                 }
    #             ]
    #         }
    #     ],
    #     "accepted": False,
    #     "owner": "1231njzxdq4"
    # }

    opcr_record = OPCR(**data)
    opcr_record.save()

    return {
        'message': "New OPCR record created",
        "id": str(opcr_record.id)
    }

# Get all the OPCR records
@app.route('/get/opcr', methods = ['GET'])
def get_opcr():
    target = OPCR.objects()
    if target:
        result = target.to_json()
        return json.loads(result)    
    return {'message': 'No OPCR record found'}

# Get an OPCR record based on ID
@app.route('/get/opcr/<id>', methods = ['GET'])
def opcr_by_id(id):
    target = OPCR.objects(id=id).first()
    if target:
        result = target.to_json()
        return json.loads(result)    
    return {'message': 'OPCR record not found'}


# create campus record (sample route only for testing purposes)
@app.route('/create/campus', methods = ["POST"])
def create_campus():
    data = request.get_json(force=True)
    # data = {
    #     'name': 'sample campus',
    #     'offices': [
    #         {
    #             'name': 'sample office #1',
    #             'head': 'sample head #1',
    #             'opcr': ['id1', 'id2']
    #         }
    #     ]
    # }
    campus = Campuses(**data)
    campus.save()
    return {
        'message': "Campus created",
        'id': str(campus.id)
    }



# read campus in db 
@app.route('/get/campus', methods=['GET'])
def get_campus():
    campuses = Campuses.objects()
    if campuses:
        return json.loads(campuses.to_json())
    return {'message': 'No campus record found'}

# read campus in db based on id attribute (sample route only for testing purposes)
@app.route('/get/campus/<id>', methods = ['GET'])
def campus_by_id(id):
    campus_record = Campuses.objects(id=id).first()
    if campus_record:
        return json.loads(campus_record.to_json())
    return {'message': 'Campus not found'}

    