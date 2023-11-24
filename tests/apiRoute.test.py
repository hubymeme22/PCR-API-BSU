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
from mongoengine.connection import disconnect
from dotenv import load_dotenv
import requests
import dbreset
import os

load_dotenv()
connect(os.getenv('MONGODB_DB'), host=f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PW')}@{os.getenv('MONGODB_HOST')}/?retryWrites=true", alias='api-test')

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
print()
print('======================')
print('ADMIN TESTING STARTED')
print('======================')

# admin login test
response = requests.post(f'{url}/login', json={'email': 'admin', 'password': 'admin'})

if (response.status_code == 200):
    print('[+] Admin login successful')
    admintoken = response.json().get('token')
else:
    print('[-] Admin login not successful')
    interrupt()

# testing for account creation
for i in range(len(sampleAccounts)):
    response = requests.post(f'{url}/api/admin/create/{sampleAccounts[i]["permission"]}', json=sampleAccounts[i], cookies={'token': admintoken})
    if (response.status_code == 200):
        print(f'[+] Account {sampleAccounts[i]["username"]}... ok')
        continue

    print(f'[-] Account {sampleAccounts[i]["username"]}... error {response.status_code}')
    interrupt()

# test to retrieve all the accounts on admin side
response = requests.get(f'{url}/api/admin/accounts/', cookies={'token': admintoken})
if (response.status_code == 200):
    print('[+] Account retrieval... ok')
    accountData: list = response.json()
else:
    print('[-] Account retrieval... failed')
    interrupt()

# find the head account and assign to the campus that will be created
# also assign the head as superior of individual that will be generated
accounts = accountData['data']
headAccount = None

# finding the first registered head
for acc in accounts:
    if (acc['permission'] == 'head'):
        print(f'[+] Head account found with id of: {acc["_id"]["$oid"]}... ok')
        headAccount = acc
        break

if (headAccount != None):
    headID = headAccount['_id']['$oid']

    # individual account creation
    response = requests.post(
        url=f'{url}/api/admin/create/individual',
        cookies={'token': admintoken},
        json={
        'email': 'samplehead@gmail.com',
        'name': 'sample head lastname',
        'username': 'sample head account',
        'password': '123abc',
        'superior': headID
    })

    if (response.status_code == 200):
        print('[+] Individual account creation... ok')
    else:
        print('[-] Individual account creation... failed')
        interrupt()

    # campus creation and assigning head
    sampleCampus.update({
        'offices': [{
            'name': 'CICS',
            'head': headID,
            'opcr': []
        }]
    })

    response = requests.post(f'{url}/api/admin/create/campus', json=sampleCampus, cookies={'token': admintoken})

    if (response.status_code == 200):
        print('[+] New Campus creation... ok')
    else:
        print('[-] New Campus creation... failed')
        interrupt()

else:
    print('[-] No head id retrieved... failed')
    interrupt()


# finding the first pmt account from the list
pmtAccount = None
for acc in accounts:
    if (acc['permission'] == 'pmt'):
        print(f'[+] PMT account found with id of: {acc["_id"]["$oid"]}... ok')
        pmtAccount = acc
        break

# assign the pmt to the sample campus
response = requests.post(f'{url}/api/admin/assign/campus', cookies={'token': admintoken}, json={
    'campus': sampleCampus['name'],
    'pmtid': pmtAccount['_id']['$oid']
})

if (response.status_code == 200):
    print('[+] PMT Campus assigning... ok')
else:
    print('[+] PMT Campus assigning... failed')
    print(response.content)
    interrupt()


##########################
#   office head testing  #
##########################
print()
print('====================')
print('HEAD TESTING STARTED')
print('====================')

response = requests.post(f'{url}/login', json={'email': 'samplehead@gmail.com', 'password': '123abc'})
if (response.status_code == 200):
    print('[+] Head login successful')
    headtoken = response.json().get('token')
else:
    print('[-] Head login not successful')
    interrupt()

# new opcr content for head account
newOpcrContent = [{
        'name': 'MFO and Target name',
        'success': [{
                'indicator': 'this is indicator 1',
                'budget': 0.0,
                'division': '',
                'accomplishment': '',
                'rating': [],
                'remarks': [],
                'assigned_to': []
        }]
}]

# creation of opcr for head account
response = requests.post(f'{url}/api/head/create/opcr', json=newOpcrContent, cookies={'token': headtoken})
if (response.status_code == 200):
    print('[+] new head opcr creation... ok')
else:
    print('[-] new head opcr creation... ok')
    print(response.content)
    interrupt()

# retrieval of new opcr added
response = requests.get(f'{url}/api/head/opcr', cookies={'token': headtoken})
if (response.status_code == 200):
    print('[+] head opcr retrieval... ok')
    print(response.json().get('data'))
else:
    print(response.content)
    print('[-] head opcr retrieval... failed')
    interrupt()

disconnect()