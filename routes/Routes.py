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

def root():
    return jsonify({
        'message': 'Welcome to PCR-API, this is the flask implementation of the previous system (OPCR) and is expanded its functionality for office head, individuals, and pmt.',
        'api_routes': {
            '/': 'contains the welcome message'
        }
    })

# returns all the account info from the database
# excluding the password
def adminAccount():
    return jsonify({
        'data': [{
            '_id': '0aec3b21ea123',
            'username': 'juandelacruz',
            'permission': 'head'
        }],
        'error': None
    })

# returns the account info from the database where user
# having the spcified id
def adminAccountWithID(id):
    return jsonify({
        'data': {
            '_id': '0aec3b21ea123',
            'username': 'juandelacruz',
            'permission': 'head'
        },
        'error': None
    })
