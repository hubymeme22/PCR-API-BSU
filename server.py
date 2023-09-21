import sys
sys.path.append('routes')

from flask import Flask
import LoginRoutes
import Routes

app = Flask(__name__)

#################################################
#  Implementation of routes from Routes module  #
#################################################
@app.route('/')
def root():
    return Routes.root()

#################################
#  Admin routes implementation  #
#################################
@app.route('/admin/account')
def adminAccount():
    return Routes.adminAccount()

@app.route('/admin/account/<id>')
def adminAccountWithID(id):
    return Routes.adminAccountWithID(id)

@app.route('/admin/login')
def adminlogin():
    return LoginRoutes.adminLogin()

@app.route('/admin/account/create/pmt', methods=['POST'])
def adminCreateAccountPMT():
    return Routes.adminCreateAccountPMT()

@app.route('/admin/account/create/head', methods=['POST'])
def adminCreateAccountHead():
    return Routes.adminCreateAccountHead()

@app.route('/admin/account/create/indiv', methods=['POST'])
def adminCreateAccountIndiv():
    return Routes.adminCreateAccountIndiv()

################################
#  Head routes implementation  #
################################
app.run()