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
from app.database.models import Campus, Office


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
    
# creates a new campus
@app.route('/admin/create/campus', methods=['POST'])
def adminCreatecampus():
    campusDetails = request.get_json(force=True)
    name = campusDetails['name']
    offices = campusDetails['offices']
    
    listOfOffices =[]
    for office_name, office_data in offices.items():  # Iterate through dictionary items
        office_name = office_data['name']             # key and value
        head_id = office_data['head']
        opcr_id = office_data.get('opcr_id', [])
        
        head = Accounts.objects(id=head_id).first()

        if head:
            office = Office(name=office_name, head=head, opcr_ids=opcr_id)
            listOfOffices.append(office)
        else:
            return jsonify({'error': 'Account not found'}), 404

    new_campus = Campus(name=name, offices=offices)
    new_campus.save()
    
    return jsonify({
        'id': str(new_campus.id),
        'name': str(new_campus.name),
        'created': True,
        'error': None
    }), 201

# returns the campus info from the database
@app.route('/admin/get/<string:campus_id>')
def adminGetCampus(campus_id):
    campus = Campus.objects(id=campus_id).first()
    if campus:
        data = {
        'data': campus.to_json(),
        'error': None
        }
        return data
    else:
        return jsonify({'error': 'Campus not found'}), 404

# returns all the campuses info from the database
@app.route('/admin/get/all-campuses', methods=['GET'])
def adminGetAllCampuses():
    campuses = Campus.objects().all()
    campus_list = [campus.to_json() for campus in campuses]
    data = {
        'data': campus_list,
        'error': None
    }
    return data

# deletes a campus by ID
@app.route('/admin/delete/campus/<string:campus_id>', methods=['DELETE'])
def adminDeleteCampus(campus_id):
    campus = Campus.objects(id=campus_id).first()
    if campus:
        campus.delete()
        return jsonify({'message': 'Campus deleted successfully'}), 200
    else:
        return jsonify({'error': 'Campus not found'}), 404