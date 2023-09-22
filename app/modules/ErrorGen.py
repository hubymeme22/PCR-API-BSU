'''
In this section, different response generated errors will be defined
'''

from flask import jsonify

def invalidRequestError(datavalue='', error='InvalidRequest'):
    return jsonify({
        'data': datavalue,
        'error': error
    })
