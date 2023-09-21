import sys
sys.path.append('../modules')

from flask import jsonify, request
import ErrorGen

def adminLogin():
    jsonData = request.get_json(force=True)
    if (not jsonData): return ErrorGen.invalidRequestError()

    username = jsonData['username']
    password = jsonData['password']
    # match username and password from the database here...

    return jsonify({
        'loggedin': True,
        'token': '0a1b2c3d4e5f67890',
        'error': None
    })
