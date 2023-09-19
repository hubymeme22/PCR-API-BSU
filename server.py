import sys
sys.path.append('routes')

from flask import Flask
import Routes

app = Flask(__name__)

#################################################
#  Implementation of routes from Routes module  #
#################################################
@app.route('/')
def root(): return Routes.root()

app.run()