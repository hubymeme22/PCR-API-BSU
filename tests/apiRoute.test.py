'''
When running this, the program will simply reset and load the sample values in the database,
make sure to run this in a test env or backup the values if running in the main database

Sequence of process for testing:
    1. login admin account
    2. create accounts with different permissions
    3. test the api routes for pmt
    4. test the api routes for head
    5. test the api routes for individuals

- Huberto
'''
from mongoengine import connect
from dotenv import load_dotenv
import requests
import dbreset
import os

load_dotenv()
connect(os.getenv('MONGODB_DB'), host=f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PW')}@{os.getenv('MONGODB_HOST')}/?retryWrites=true&w=majority&appName=AtlasApp")

# change this part
apiServerIP = '127.0.0.1'
apiServerPORT = 5000

url = f'http://{apiServerIP}:{apiServerPORT}'
interruption = True

# for interruption
def interrupt():
    if (interruption and input('Continue testing? y/n: ').capitalize() == 'N'):
        exit()


################################
#  Declaration of sample data  #
################################
# accounts that will be registered by the admin
sampleAccounts = [
    {
        'email': 'samplepmt@gmail.com',
        'name': 'sample pmt lastname',
        'username': 'sample pmt account',
        'password': '123abc',
        'permission': 'pmt'                 # not needed, for automation purposes
    },
    {
        'email': 'samplehead@gmail.com',
        'name': 'sample head lastname',
        'username': 'sample head account',
        'password': '123abc',
        'permission': 'head'
    }
]

# campus where head will be assigned later
sampleCampus = {
    'name': 'Alangilan',
    'offices': [
        {
            'name': 'CICS',
            'head': '',
            'opcr': []
        }
    ]
}

dbreset.dbReset()

###################
#  admin testing  #
###################
print('======================')
print('ADMIN TESTING STARTED')
print('======================')

# admin login test
print('[*] Logging in admin account')
response = requests.post(f'{url}/login', json={'email': 'admin', 'password': 'admin'})

if (response.status_code == 200):
    print('[+] Admin login successful')
    admintoken = response.json().get('token')
else:
    print('[-] Admin login not successful')
    interrupt()

# testing for account creation
print('[*] Testing admin account creation...')
for i in range(len(sampleAccounts)):
    response = requests.post(f'{url}/api/admin/create/{sampleAccounts[i]["permission"]}', json=sampleAccounts[i])
    if (response.status_code == 200):
        print(f'[+] Account {sampleAccounts[i]["username"]}... ok')
        continue

    print(f'[-] Account {sampleAccounts[i]["username"]}... error {response.status_code}')
    interrupt()

# test to retrieve all the accounts on admin side
print('[*] Testing admin\'s account retrieval...')
response = requests.get(f'{url}/api/admin/accounts/')
if (response.status_code == 200):
    print('[+] Account retrieval... success')
    accountData: list = response.json()
else:
    print('[-] Account retrieval... failed')
    interrupt()

# find the head account and assign to the campus that will be created
# also assign the head as superior of individual that will be generated
accounts = accountData['data']
headAccount = None

# finding the first registered head
print('[*] Retrieving head account...')
for acc in accounts:
    if (acc['permission'] == 'head'):
        print(f'[+] Head account found with id of: {acc["_id"]["$oid"]}')
        headAccount = acc
        break

if (headAccount != None):
    headID = headAccount['_id']['$oid']
    print('[*] Assigning head to individual account...')

    # individual account creation
    response = requests.post(
        url=f'{url}/api/admin/create/individual',
        json={
        'email': 'samplehead@gmail.com',
        'name': 'sample head lastname',
        'username': 'sample head account',
        'password': '123abc',
        'superior': headID
    })

    if (response.status_code == 200):
        print('[+] Individual account created!')
    else:
        print('[-] Individual account not created')
        interrupt()

    # campus creation and assigning head
    sampleCampus.update({
        'offices': [{
            'name': 'CICS',
            'head': headID,
            'opcr': []
        }]
    })

    print('[*] Creating new campus...')
    response = requests.post(f'{url}/api/admin/create/campus', json=sampleCampus)
    print(response.content)
    if (response.status_code == 200):
        print('[+] New Campus created!')
    else:
        print(response.json())
        print('[-] Campus not added!')
        interrupt()

else:
    print('[-] No head id retrieved')
    interrupt()