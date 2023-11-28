'''
    This file will contain the routes and their specific procedures,
    when complex (ofc, not the basic ones) procedures are need to
    be added such as CRUD with complex computation, summarization, etc.
    these part will be added on modules folder.

    Also, please sort the functions below by its function name.

    Happy coding :>
    - Hubert
'''
from app.modules import Admin, PMT, Head
from app import app

@app.route("/")
def root():
    return {
        'message': 'Welcome to PCR-API, this is the flask implementation of the previous system (OPCR) and is expanded its functionality for office head, individuals, and pmt.',
        'api_routes': {
            '/': 'contains the welcome message'
        }
    }

############################################
#   Admin functionalities implementation   #
############################################
@app.route('/api/admin/accounts/')
def adminAccount():
    return Admin.adminAccount()

@app.route('/api/admin/accounts/head')
def adminHeadAccount():
    return Admin.adminHeadAccount()

@app.route('/api/admin/accounts/head/unassigned')
def adminUnassignedHeadAccount():
    return Admin.adminUnassignedHeadAccount()

@app.route('/api/admin/account/<id>')
def adminAccountWithID(id):
    return Admin.adminAccountWithID(id)

# account creation part
@app.route('/api/admin/create/pmt', methods=['POST'])
def adminCreateAccountPMT():
    return Admin.adminCreateAccountPMT()

@app.route('/api/admin/create/head', methods=['POST'])
def adminCreateAccountHead():
    return Admin.adminCreateAccountHead()

@app.route('/api/admin/create/individual', methods=['POST'])
def adminCreateAccountIndiv():
    return Admin.adminCreateAccountIndiv()

# campus CRUD operation part
@app.route('/api/admin/create/campus', methods=['POST'])
def adminCreateCampus():
    return Admin.adminCreateCampus()

@app.route('/api/admin/campuses')
def adminCampuses():
    return Admin.adminGetCampuses()

@app.route('/api/admin/departments/<campusid>')
def adminGetDepartmentsByCampus(campusid):
    return Admin.adminGetDepartments(campusid)

@app.route('/api/admin/edit/campus/<id>', methods=['PUT', 'POST'])
def adminEditCampus(id):
    return Admin.adminEditCampusData(id)

@app.route('/api/admin/delete/campus/<id>', methods=['GET', 'DELETE'])
def adminDeleteCampus(id):
    return Admin.adminDeleteCampus(id)

@app.route('/api/admin/delete/office/<campusid>/<officeid>', methods=['GET', 'DELETE'])
def adminDeleteDepartment(campusid, officeid):
    return Admin.adminDeleteOffice(campusid, officeid)

# assign pmt to a campus
@app.route('/api/admin/assign/pmt/campus', methods=['POST', 'PUT'])
def adminAssignPmtCampus():
    return Admin.adminAssignPmtCampus()

# assign head to a department
@app.route('/api/admin/assign/head/campus', methods=['POST', 'PUT'])
def adminAssignHeadCampus():
    return Admin.adminAssignHeadCampus()

##########################################
#   PMT functionalities implementation   #
##########################################
# create new target record (sample route only for testing purposes)
@app.route('/api/pmt/create/opcr', methods = ["POST"])
def create_opcr():
    return PMT.create_opcr()

# Get all the OPCR records
# @app.route('/api/pmt/get/opcr', methods = ['GET'])
# def get_opcr():
#     return PMT.get_opcr()

# Get an OPCR record based on ID
@app.route('/api/pmt/get/opcr/<id>', methods = ['GET'])
def opcr_by_id(id):
    return PMT.opcr_by_id(id)

# Get OPCR record(s) based on the offices of the Campus(es) of logged in PMT
@app.route('/api/pmt/get/opcr', methods = ['GET'])
def get_opcr():
    return PMT.opcr_by_campus()

# create campus record (sample route only for testing purposes)
@app.route('/api/pmt/create/campus', methods = ["POST"])
def create_campus():
    return PMT.create_campus()

# read campus in db 
@app.route('/api/pmt/get/campuses', methods=['GET'])
def get_campus():
    return PMT.get_campus()

# read campus in db based on id attribute (sample route only for testing purposes)
@app.route('/api/pmt/get/campus/<id>', methods = ['GET'])
def campus_by_id(id):
    return PMT.campus_by_id(id)

@app.route('/api/pmt/update/opcr/<id>', methods = ['POST'])
def write_remark(id):
    return PMT.write_remark(id)

###########################################
#   Head functionalities implementation   #
###########################################
@app.route('/api/head/create/opcr', methods=['POST'])
def createHeadOPCR():
    return Head.createOPCR()

@app.route('/api/head/opcr')
def retrieveUserOPCR():
    return Head.retrieveUserOPCR()
