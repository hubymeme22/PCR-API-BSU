'''
In this section, different response generated errors will be defined
'''

# error response generation
def invalidRequestError(datavalue='', error='InvalidRequest', statusCode=400):
    return ({'data': datavalue, 'error': error}, statusCode)

# checks for the request missing parameters
def parameterCheck(requiredParams: list, jsonRequest: dict):
    if (requiredParams == None): return ['NoParamsProvided']
    requestKeys = jsonRequest.keys()
    missingParams = []

    for key in requiredParams:
        if (key not in requestKeys):
            missingParams.append(key)
    return missingParams