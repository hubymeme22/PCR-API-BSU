from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
import os

# Initiate flask app
app = Flask(__name__)
cors = CORS(app)

# Load environment variables (in .env)
load_dotenv()

# Connect to mongodb
connect(os.getenv('MONGODB_DB'), host=f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PW')}@{os.getenv('MONGODB_HOST')}/?retryWrites=true&w=majority&appName=AtlasApp")