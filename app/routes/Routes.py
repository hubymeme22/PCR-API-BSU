'''
    This file will contain the routes and their specific procedures,
    when complex (ofc, not the basic ones) procedures are need to
    be added such as CRUD with complex computation, summarization, etc.
    these part will be added on modules folder.

    Also, please sort the functions below by its function name.

    Happy coding :>
    - Hubert
'''
from app.modules import Admin, PMT
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
@app.route('/api/admin/accounts')
def adminAccount():
    return Admin.adminAccount()

@app.route('/api/admin/account/<id>')
def adminAccountWithID(id):
    return Admin.adminAccountWithID(id)

@app.route('/api/admin/create/pmt', methods=['POST'])
def adminCreateAccountPMT():
    return Admin.adminCreateAccountPMT()

@app.route('/api/admin/create/head', methods=['POST'])
def adminCreateAccountHead():
    return Admin.adminCreateAccountHead()

@app.route('/api/admin/create/indiv', methods=['POST'])
def adminCreateAccountIndiv():
    return Admin.adminCreateAccountIndiv()


##########################################
#   PMT functionalities implementation   #
##########################################
# create new target record (sample route only for testing purposes)
@app.route('/api/pmt/create/opcr', methods = ["POST"])
def create_opcr():
    return PMT.create_opcr()

# Get all the OPCR records
@app.route('/api/pmt/get/opcr', methods = ['GET'])
def get_opcr():
    return PMT.get_opcr()

# Get an OPCR record based on ID
@app.route('/api/pmt/get/opcr/<id>', methods = ['GET'])
def opcr_by_id(id):
    return PMT.opcr_by_id(id)

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