from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

load_dotenv()
DATABASE_NAME = os.getenv('MONGODB_DB')
# DBConnection: MongoClient = MongoClient("localhost", 27017)
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
    def addDepartmentOpcr(campusid: str, officeid: str, opcrid: str):
        return CampusesConnection.update_one({'_id': ObjectId(campusid), 'offices._id': ObjectId(officeid)}, {
            '$push': {'offices.$.opcr': ObjectId(opcrid)}
        })

    def getAllCampuses():
        return CampusesConnection.find()

    def getCampusDetails(campusid: str):
        return CampusesConnection.find_one({'_id': ObjectId(campusid)})

    def getCampusDetailsByOfficeId(officeid: str):
        return CampusesConnection.find_one({
            'offices._id': ObjectId(officeid)
        })

    def getPmtCampus(pmtid: str):
        return CampusesConnection.find_one({
            'pmt': ObjectId(pmtid)
        })

    def getHeadCampus(headid: str):
        return CampusesConnection.find_one({'offices.head': ObjectId(headid)})

    def getHeadOffice(headid: str):
        matchedCampus = CampusesFunctionalities.getHeadCampus(headid)
        for offices in matchedCampus['offices']:
            if (offices['head'] == headid):
                return offices

    def createNewCampus(campusData: dict):
        campusData.update({'_id': ObjectId()})
        campusData['offices'] = [formatObjectValues(office) for office in campusData['offices']]
        return CampusesConnection.insert_one(campusData)

    def deleteCampusByID(campusid: str):
        return CampusesConnection.delete_one({'_id': ObjectId(campusid)})

#######################################
#  ACCOUNTS DATABASE FUNCTIONALITIES  #
#######################################
class AccountDBFunctionalities:
    def createAccount(accountData: dict):
        accountData.update({'_id': ObjectId()})
        return AccountConnection.insert_one(accountData)

    def getAccountsByPermission(permission: str):
        return AccountConnection.find({'permission': permission})

    def getAllAccounts():
        return AccountConnection.find()

    def getSpecificAccount(accid: str):
        return AccountConnection.find_one({'_id': ObjectId(accid)})

    def deleteAccount(accid: str):
        return AccountConnection.delete_one({'_id': ObjectId(accid)})

    def updateAccount(accid: str, accountData: dict):
        return AccountConnection.update_one({'_id': accid}, accountData)

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

    def createOpcrForUser(userid: str, target: dict):
        return OPCRConnection.insert_one({
            '_id': ObjectId(),
            'targets': [target],
            'owner': ObjectId(userid),
            'archived': False,
            'accepted': False,
            'status': 'in progress'
        })

    def updateMFOByID(opcrid: str, mfoid: str, update: dict):
        try:
            return OPCRConnection.update_many(
                {
                    '_id': ObjectId(opcrid),
                    'targets._id': ObjectId(mfoid)
                },
                { '$set': { 'targets.$': update }},
                upsert=True)
        except Exception as e:
            return None

###########################
#  ADMIN FUNCTIONALITIES  #
###########################
class AdminFunctionalities:
    def assignPmtToCampus(pmtid: str, campusid: str):
        campusDetails = CampusesFunctionalities.getCampusDetails(campusid)
        if (campusDetails == None):
            raise Exception('NonexistentCampus')

        pmtAccount = AccountDBFunctionalities.getSpecificAccount(pmtid)
        if (pmtAccount == None):
            raise Exception('NonexistentPMTAccount')

        if (pmtAccount.get('permission') != 'pmt'):
            raise Exception('PMTPermissionError')

        return CampusesConnection.update_one({'_id': ObjectId(campusid)}, {
            '$push': { 'pmt': ObjectId(pmtid) }
        })

    def assignHeadToDepartment(headid: str, campusid: str, officeid: str):
        campusDetails = CampusesConnection.find_one({
            '_id': ObjectId(campusid),
            'offices._id': ObjectId(officeid)
        })

        if (campusDetails == None):
            raise Exception('NonexistentCampus')

        pmtAccount = AccountDBFunctionalities.getSpecificAccount(headid)
        if (pmtAccount == None):
            raise Exception('NonexistentPMTAccount')

        if (pmtAccount.get('permission') != 'head'):
            raise Exception('PMTPermissionError')

        return CampusesConnection.update_one({
            '_id': ObjectId(campusid),
            'offices._id': ObjectId(officeid)
        },{
            '$set': {'offices.$.head': ObjectId(headid)}
        }, upsert=True)

##########################
#  HEAD FUNCTIONALITIES  #
##########################
class HeadFunctionalities:
    def getOpcrData(userid: str) -> dict:
        return OPCRConnection.find_one({
            'owner': ObjectId(userid),
            'archived': False
        })

    def getAllOPCR(userid: str) -> list:
        return OPCRConnection.find({
            'owner': userid
        })

    def appendNewMFO(opcrid: str, mfodata: dict):
        opcrData = OPCRFunctionalities.getOneOpcr(opcrid)
        if (opcrData == None): return None

        mfodata = formatObjectValues(mfodata)
        mfodata['success'] = [formatObjectValues(success, 'oid') for success in mfodata['success']]
        return OPCRFunctionalities.addOneTarget(opcrid, mfodata)

    def createMFO(userid: str, mfodata: dict):
        mfodata = formatObjectValues(mfodata)
        mfodata['success'] = [formatObjectValues(success, 'oid') for success in mfodata['success']]
        return OPCRFunctionalities.createOpcrForUser(userid, mfodata)

    def updateMFO(userid: str, mfoid: str, mfodata: dict):
        mfodata = formatObjectValues(mfodata)
        mfodata['success'] = [formatObjectValues(success, 'oid') for success in mfodata['success']]

        headOpcrData = HeadFunctionalities.getOpcrData(userid)
        if (headOpcrData == None): return

        headOpcrID = headOpcrData['_id']
        return OPCRFunctionalities.updateMFOByID(headOpcrID, mfoid, mfodata)

#########################
#  PMT FUNCTIONALITIES  #
#########################
class PMTFunctionalities:
    def getOpcrData(userid: str):
        campusAssigned = CampusesConnection.find_one({'pmt': ObjectId(userid)})
        if (campusAssigned == None): return []

        # head account retrieval
        headAccounts = []
        for office in campusAssigned['offices']:
            if (office.get('head')):
                headAccounts.append(office['head'])

        # opcr retrieval of all the head accounts
        return OPCRConnection.find({'owner': {'$in': headAccounts}})

    def getOpcrDataByOfficeID(officeid: id):
        campusAssigned = CampusesFunctionalities.getCampusDetailsByOfficeId(officeid)
        if (campusAssigned == None): raise Exception('NonexistentOfficeID')

        for office in campusAssigned['offices']:
            if (office['_id'].__str__() == officeid):
                opcrId = office['opcr'][-1]
                return OPCRFunctionalities.getOneOpcr(opcrId.__str__())
        return None