from utils import message
from Crypto.Cipher import AES
import json
import datetime

def authorize(request, APP_SECRET, NONCE, users_collection):
    ## Check if token and tag are present in request
    if 'token' not in request.headers or 'tag' not in request.headers:
        return {
            'error': True,
            'code': 401, 
            'message': 'Token or tag not provided',
            'err': 'Unauthorized'
        }

    token = request.headers['token']   
    tag = request.headers['tag']    

    key = APP_SECRET.encode('utf-8')
    ## Creating the cypher object
    cipher = AES.new(key, AES.MODE_EAX, nonce=NONCE.encode('utf-8'))

    ## Decrypting the token
    data = cipher.decrypt(bytes.fromhex(token))

    ## Converting the decrypted token to a python object
    data_object = json.loads(data.decode('utf-8'))

    ## Checking if the decrypted token has the required fields
    if 'username' not in data_object or 'expiry' not in data_object:
        return {
            'error': True,
            'code': 401, 
            'message': 'Invalid token',
            'err': 'Unauthorized'
        }

    ## Checking if the token has expired
    if data_object['expiry'] < datetime.datetime.timestamp(datetime.datetime.now()):
        return {
            'error': True,
            'code': 401, 
            'message': 'Token expired',
            'err': 'Unauthorized'
        }
    
    try:
        ## Verifying the integrity of the tag
        cipher.verify(bytes.fromhex(tag))

        ## Checking if the user exists in the database
        cursor = users_collection.find({"username": data_object['username']})
        users = list(cursor)

        if len(users) == 0:
            ## If the user does not exist, return error
            return {
            'error': True,
            'code': 401, 
            'message': 'Invalid Credentials',
            'err': 'Unauthorized'
        }
        else:
            ## If the user exists, return the user object
            return {
                'error': False,
                'code': 200,
                'message': 'Valid Token',
                'username': data_object['username'],
                'licenseID': users[0]['licenseID']
            }
    except:
        ## If the tag is invalid, return error
        return {
            'error': True,
            'code': 401,
            'message': 'Invalid Token',
            'err': 'Unauthorized'
        }