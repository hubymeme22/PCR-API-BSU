from app.database.models import Sessions, Accounts
from app.modules import ErrorGen
from flask import request
from datetime import datetime, timedelta
from uuid import uuid4
import json

# stores the session on the database
def login(email, password):
    userlogin = Accounts.objects(email=email, password=password).first()
    if (userlogin == None):
        return ({
            'error': 'NonexistentAccount',
            'loggedIn': False,
            'permission': None,
            'token': ''
        }, 401)

    userlogin = json.loads(userlogin.to_json())
    generatedToken = str(uuid4())

    # generates a new session after loging in
    session = Sessions(
        userid=userlogin['_id']['$oid'],
        token=generatedToken,
        permission=userlogin['permission'],
        expiration=datetime.now() + timedelta(hours=1))

    session.save()
    return {
        'error': None,
        'loggedIn': True,
        'permission': userlogin['permission'],
        'token': generatedToken
    }

# retrieves the user session information based on token
def getSessionInfo(token):
    if (token == None): return None
    session = Sessions.objects(token=token).first()

    if (session == None): return None
    return json.loads(session.to_json())

# retrieves and refreshes by returning new token
def refreshToken(token):
    session = Sessions.objects(token=token).first()
    if (session == None): return ErrorGen.invalidRequestError(
        error='NonexistentToken',
        statusCode=401)

    generatedToken = str(uuid4())
    session = session.to_json()

    session = Sessions(
        userid=session['userid'],
        token=generatedToken,
        permission=session['permission'],
        expiration=datetime.now() + timedelta(days=1))
    session.save()

    # delete the old token here...
    return {
        'error': None,
        'newtoken': generatedToken
    }

# checks token from request
def requestTokenCheck(permission):
    token = request.headers.get('Authorization')
    if (token == None):
        return ErrorGen.invalidRequestError(
            error='NoCookie',
            statusCode=403)

    sessinfo = getSessionInfo(token)
    if (sessinfo == None):
        return ErrorGen.invalidRequestError(
            error='ExpiredCookie',
            statusCode=403)

    if (sessinfo['permission'] != permission):
        return ErrorGen.invalidRequestError(
            error='InvalidPermission',
            statusCode=403)