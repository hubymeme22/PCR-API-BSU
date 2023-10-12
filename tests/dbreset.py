import sys
sys.path.append('..')

from app.database.models import Accounts, OPCR, Campuses, Sessions
from mongoengine import connect
from dotenv import load_dotenv
import os

load_dotenv()
connect(os.getenv('MONGODB_DB'), host=f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PW')}@{os.getenv('MONGODB_HOST')}/?retryWrites=true&w=majority&appName=AtlasApp")

def dbReset():
    try:
        print('[*] Dropping Accounts collection...')
        Accounts.drop_collection()
        print('[+] Dropping Accounts collection... ok')

        print('[*] Dropping OPCR collection...')
        OPCR.drop_collection()
        print('[+] Dropping Accounts collection... ok')

        print('[*] Dropping Campuses collection...')
        Campuses.drop_collection()
        print('[+] Dropping Campuses collection... ok')

        print('[*] Dropping Sesssions collection...')
        Sessions.drop_collection()
        print('[+] Dropping Sessions collection... ok')

        print('[*] Appending default admin credentials...')
        Accounts(
            name='admin',
            username='admin',
            email='admin',
            password='admin',
            permission='admin').save()
        print('[*] Appending default admin credentials... ok')

    except Exception as e:
        print(f'[-] An error occured: {e}')

if (__name__ == '__main__'):
    dbReset()