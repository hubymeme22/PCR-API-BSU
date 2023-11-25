'''
The purpose of this file is to automatically insert campuses and its departments
for development testing purposes.
'''
import requests as re

# api endpoint details
apiServerIP = '127.0.0.1'
apiServerPORT = 5000
url = f'http://{apiServerIP}:{apiServerPORT}'

# campus where head will be assigned later
sampleCampus = [
    {
        'name': 'Alangilan',
        'offices': [
            { 'name': 'CICS', 'head': '', 'opcr': [] },
            { 'name': 'COE', 'head': '', 'opcr': [] },
            { 'name': 'CEAFA', 'head': '', 'opcr': [] },
            { 'name': 'OSA', 'head': '', 'opcr': [] },
            { 'name': 'External Office', 'head': '', 'opcr': [] }
        ]
    },
    {
        'name': 'Pablo Borbon',
        'offices': [
            { 'name': 'CoM', 'head': '', 'opcr': [] },
            { 'name': 'OSA', 'head': '', 'opcr': [] },
            { 'name': 'External Office', 'head': '', 'opcr': [] }
        ]
    },
    {
        'name': 'Malvar',
        'offices': [
            { 'name': 'CICS', 'head': '', 'opcr': [] },
            { 'name': 'OSA', 'head': '', 'opcr': [] },
            { 'name': 'External Office', 'head': '', 'opcr': [] }
        ]
    }
]


print('[*] Logging in admin account...')

# login admin account to use token permission
response = re.post(f'{url}/login', json={
    'email': 'admin',
    'password': 'admin'
})

if (response.status_code != 200):
    print('[-] unsuccessful admin login')
    exit()

print('[+] admin account logged in!')
response = response.json()
print(f'[+] using token: {response["token"]}')

# loop through campuses to append the campus
for campusData in sampleCampus:
    re.post(f'{url}/api/admin/create/campus', json=campusData, cookies={'token': response['token']})