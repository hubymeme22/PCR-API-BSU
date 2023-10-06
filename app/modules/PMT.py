from flask import request
from app.database.models import Campuses, OPCR
import json

# create new target record (sample route only for testing purposes)
def create_opcr():
    data = request.get_json(force=True)
    opcr_record = OPCR(**data)
    opcr_record.save()

    return {
        'status': 'created',
        'id': str(opcr_record.id)
    }

# Get all the OPCR records
def get_opcr():
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


# create campus record (sample route only for testing purposes)
def create_campus():
    data = request.get_json(force=True)
    campus = Campuses(**data)
    campus.save()
    return {
        'error': None,
        'id': str(campus.id)
    }

# read campus in db 
def get_campus():
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