from flask import request
from app.database.models import Campuses, OPCR, Accounts
from app.modules import ErrorGen, Sessions
from bson import ObjectId
import json

# create new target record (sample route only for testing purposes)
def create_opcr():
    # Get basic user info from cookie token    
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Save data from POST request
    data = request.get_json(force=True)
    opcr_record = OPCR(**data)
    opcr_record.save()

    return {
        'status': 'created',
        'id': str(opcr_record.id)
    }

# Get all the OPCR records
def get_opcr():
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Fetch all OPCR objects
    target = OPCR.objects()
    if target:
        result = target.to_json()
        return {
            'data': json.loads(result),
            'error': None
        }

    return {
        'data': [],
        'error': None
    }

# Get an OPCR record based on ID
def opcr_by_id(id):
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Check validity of ID format
    if not ObjectId.is_valid(id):
        return ErrorGen.invalidRequestError(error=f"Invalid id ('{id}'). It must be a 12-byte value. See https://www.mongodb.com/docs/manual/reference/method/ObjectId/")
    
    # Fetch the OPCR object
    target = OPCR.objects(id=id).first()
    if target:
        result = target.to_json()
        return {
            'data': json.loads(result),
            'error': None
        }

    return {
        'data': [],
        'error': None
    }


def opcr_by_campus():
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Get the campus(es) that the pmt is assigned into
    campuses = Campuses.objects(pmt__contains=user_info['userid']).to_json()
    
    # Get all the OPCR IDs of the campus offices
    all_opcr = []
    for campus in json.loads(campuses):
        for office in campus['offices']:
            all_opcr.extend(office['opcr'])

    # Get all the OPCR details using the OPCR IDs retreived above
    result = OPCR.objects(id__in = [ObjectId(_id) for _id in all_opcr])
    
    return {
        'data': json.loads(result.to_json())
    }, 200


# create campus record (sample route only for testing purposes)
def create_campus():
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Save data from POST request
    data = request.get_json(force=True)    
    campus = Campuses(**data)
    campus.save()
    return {
        'error': None,
        'id': str(campus.id)
    }

# read campus in db 
def get_campus():
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Fetch Campuses objects
    campuses = Campuses.objects()
    if campuses:
        return {
            'data': json.loads(campuses.to_json()),
            'error': None
        }

    return {
        'data': [],
        'error': None
    }

# read campus in db based on id attribute (sample route only for testing purposes)
def campus_by_id(id):
    # Get basic user info from cookie token
    user_token = request.cookies.get('token')
    user_info = Sessions.getSessionInfo(user_token)
    
    # Check if the user is logged in or if the permission is set to PMT
    if not user_info or user_info['permission'] != 'pmt':
        return ErrorGen.invalidRequestError(error = 'Unauthorized Request', statusCode = 403)

    # Check validity of ID format
    if not ObjectId.is_valid(id):
        return ErrorGen.invalidRequestError(error=f"Invalid id ('{id}'). It must be a 12-byte value. See https://www.mongodb.com/docs/manual/reference/method/ObjectId/")
    
    # Fetch the Campus object
    campus_record = Campuses.objects(id=id).first()
    if campus_record:
        return {
            'data': json.loads(campus_record.to_json()),
            'error': None
        }

    return {
        'data': [],
        'error': None
    }

