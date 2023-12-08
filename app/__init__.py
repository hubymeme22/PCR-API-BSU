from flask import Flask
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
import os

# Initiate flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Load environment variables (in .env)
print('[*] Loading envirnoment variables...')
load_dotenv()

# Connect to mongodb
print(f"[+] Connecting to: mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PW')}@{os.getenv('MONGODB_HOST')}/")
connect(os.getenv('MONGODB_DB'), host=f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PW')}@{os.getenv('MONGODB_HOST')}/?retryWrites=true")
# connect(host="mongodb://localhost:27017/opcr")