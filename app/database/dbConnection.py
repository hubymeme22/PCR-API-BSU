from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

load_dotenv()
DATABASE_NAME = os.getenv('MONGODB_DB')
DBConnection: MongoClient = MongoClient(f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PW')}@{os.getenv('MONGODB_HOST')}/?retryWrites=true&w=majority&appName=AtlasApp")

# All collections connections
OPCRConnection = DBConnection.get_database(DATABASE_NAME).get_collection('o_p_c_r')
AccountConnection = DBConnection.get_database(DATABASE_NAME).get_collection('accounts')
CampusesConnection = DBConnection.get_database(DATABASE_NAME).get_collection('campuses')

# retrieves the id (for deprecated shit purposes)
def extractID(object: dict):
    try: return object.get('_id').get('$oid').replace('-', '')[:24]
    except: return ''

# checks if the object has id
def hasID(object: dict) -> bool:
    return not (object.get('_id') == None)

# formats the _id values to ObjectID
def formatObjectValues(object: dict, idtype='_id'):
    if (hasID(object)):
        object[idtype] = ObjectId(extractID(object))
        return object

    object[idtype] = ObjectId()
    return object

#######################################
#  CAMPUSES DATABASE FUNCTIONALITIES  #
#######################################
class CampusesFunctionalities:
    def getPmtCampus(pmtid: str) -> dict | None:
        return CampusesConnection.find_one({
            'pmt': {'$elemMatch': pmtid}
        })

    def getHeadCampus(headid: str) -> dict | None:
        return CampusesConnection.find_one({
            'offices': {'$elemMatch': {
                'head': headid
            }}
        })

    def getHeadOffice(headid: str) -> dict | None:
        matchedCampus = CampusesFunctionalities.getHeadCampus(headid)
        for offices in matchedCampus['offices']:
            if (offices['head'] == headid):
                return offices

###################################
#  OPCR DATABASE FUNCTIONALITIES  #
###################################
class OPCRFunctionalities:
    def getOneOpcr(opcrid: str):
        return OPCRConnection.find_one({
            '_id': ObjectId(opcrid)
        })

    def addOneTarget(opcrid: str, target: dict):
        opcrfilter = {'_id': ObjectId(opcrid)}
        return OPCRConnection.update_one(opcrfilter, {'$push': {
            'targets': target
        }})

    def createOpcrForUser(userid: str, target: dict) -> dict | None:
        return OPCRConnection.insert_one({
            '_id': ObjectId(),
            'targets': [target],
            'owner': userid,
            'archived': False,
            'accepted': False,
            'status': 'in progress'
        })

###################################
#  HEAD DATABASE FUNCTIONALITIES  #
###################################
class HeadFunctionalities:
    def getOpcrData(userid: str) -> dict:
        return OPCRConnection.find_one({
            'owner': userid,
            'archived': False
        })

    def getAllOPCR(userid: str) -> list:
        return OPCRConnection.find({
            'owner': userid
        })

    def appendNewMFO(opcrid: str, mfodata: dict) -> dict:
        opcrData = OPCRFunctionalities.getOneOpcr(opcrid)
        if (opcrData == None): return None

        mfodata = formatObjectValues(mfodata)
        mfodata['success'] = [formatObjectValues(success, 'oid') for success in mfodata['success']]
        return OPCRFunctionalities.addOneTarget(opcrid, mfodata)

    def createMFO(userid: str, mfodata: dict) -> dict:
        mfodata = formatObjectValues(mfodata)
        mfodata['success'] = [formatObjectValues(success, 'oid') for success in mfodata['success']]
        return OPCRFunctionalities.createOpcrForUser(userid, mfodata)