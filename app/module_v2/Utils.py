from bson.objectid import ObjectId

def convertToLegacy(object: dict):
    objectID: ObjectId | str = object.get('_id')
    if (objectID and ('bson' in str(type(objectID)))):
        object.update({'_id': { '$oid': object['_id'].__str__() }})
    return object

def convertLegacyToString(object: dict, field: str):
    objectID: ObjectId | str = object.get(field)
    if (objectID == None): return object
    if ('bson' in str(type(objectID))):
        object.update({field: objectID.__str__()})
        return object
    return object