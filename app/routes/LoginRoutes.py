from app.database.models import Accounts
from app.modules import ErrorGen
from flask import request
from app import app

@app.route('/login', methods=['POST'])
def login():
    jsonData = request.get_json(force=True)
    if (not jsonData): return ErrorGen.invalidRequestError()

    username = jsonData['username']
    password = jsonData['password']

    account = Accounts.objects(username=username, password=password).first()
    if (account == None):
        return {
            'loggedin': False,
            'token': None,
            'error': 'NonexistentAccount'
        }

    return {
        'loggedin': True,
        'token': '',
        'error': None
    }