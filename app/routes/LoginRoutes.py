from app.modules import ErrorGen, Sessions
from flask import request
from app import app

@app.route('/login', methods=['POST'])
def login():
    jsonData: dict = request.get_json(force=True)
    if (not jsonData): return ErrorGen.invalidRequestError()

    email = jsonData.get('email')
    password = jsonData.get('password')

    return Sessions.login(email, password)

@app.route('/refresh-token')
def refreshToken():
    token = request.cookies.get('token')
    return Sessions.refreshToken(token)