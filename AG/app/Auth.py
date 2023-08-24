
import logging
from functools import wraps
#request is from flask request
from flask import make_response, jsonify,request
LOG = logging.getLogger()
import requests as api
import json
import datetime
import os

IP_AUTH_SERVICE = "auth"
TOKEN_ORG = "ed4ade2b846402b9ae56c75e1df923c71a1a081a339dccb7fa9d2c22194ddaff" #token de xelhua

TOKEN_REQUIERD=os.getenv("TOKEN_REQUIERD") 
API_KEY=os.getenv("API_KEY") # sha256 hash (eg. "9aa491c85508cfeead30c569c88c8f26e3881792a3f158a323ee9ac6150ab1cd") 
interval_expiration = 60*48 #60 minutes * 48 hours = 2 days


SESSIONS = {API_KEY:{"expiration_date":None,"API_key":True,"tokenuser":API_KEY}} #{"access_token":"{expiration_date","tokenuser","API_key":true}}


if TOKEN_REQUIERD =="True" or TOKEN_REQUIERD =="TRUE" or TOKEN_REQUIERD =="true":
    TOKEN_REQUIERD = True
else:
    TOKEN_REQUIERD = False

# Authentication decorator
def data_autorization_requiered(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if TOKEN_REQUIERD:

            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            #LOG.debug("TOKEN: %s" %token)
            #LOG.debug(request.headers)

            if not token: # throw error if no token provided
                return make_response(jsonify({"message": "A valid token is missing!"}), 403)
            try:
                # verify token access
                #get token user assosiated to session token ()
                tokenuser = request.get_json(force=True)['data']['token_user']

                if verify_API_KEY(token):
                    pass
                else:
                    token_assosiated = getUserBy_access_token(token)
                    

                    if token_assosiated==tokenuser:
                        LOG.info("Athorized")
                        pass
                    else: #invalid token 
                        LOG.error("UNauthorized")
                        return make_response(jsonify({"message": "Unable to access!."}), 403)
            except:
                return make_response(jsonify({"message": "Invalid token!"}), 403)

        else:
            if "x-access-token" in request.headers:
                token = request.headers['x-access-token']
                token_verification = verify_session_token(token)
                LOG.info("TOKEN FOUND. is valid?: %s" %token_verification)

        return f(*args, **kwargs)
    return decorator

# Authentication decorator
def resource_autorization_requiered(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if TOKEN_REQUIERD:

            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            #LOG.debug("TOKEN: %s" %token)
            #LOG.debug(request.headers)

            if not token: # throw error if no token provided
                return make_response(jsonify({"message": "A valid token is missing!"}), 403)
            try:
                # verify token access
                #get token user assosiated to session token ()
                tokenuser = request.get_json(force=True)['auth']['user']
                if verify_API_KEY(tokenuser):
                    return True

                token_assosiated = getUserBy_access_token(token)
                LOG.debug(token_assosiated)
                LOG.debug(tokenuser)

                if token_assosiated==tokenuser:
                    LOG.debug("Athorized")
                    pass
                else: #invalid token 
                    return make_response(jsonify({"message": "Unable to access!."}), 403)
            except:
                return make_response(jsonify({"message": "Invalid token!"}), 403)

        else:
            if "x-access-token" in request.headers:
                token = request.headers['x-access-token']
                token_verification = verify_session_token(token)
                LOG.debug("TOKEN FOUND. is valid?: %s" %token_verification)

        return f(*args, **kwargs)
    return decorator


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if TOKEN_REQUIERD:

            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            #LOG.debug("TOKEN: %s" %token)
            #LOG.debug(request.headers)

            if not token: # throw error if no token provided
                return make_response(jsonify({"message": "A valid token is missing!"}), 401)
            try:
            # verify token
                token_verification = verify_session_token(token)
                #LOG.debug("token_verification: %s"% (token_verification))

                if token_verification:
                    pass
                else: #invalid token 
                    return make_response(jsonify({"message": "Token expired!."}), 401)
            except:
                return make_response(jsonify({"message": "Invalid token!"}), 401)

            # Return the user information attached to the token
        else:
            if "x-access-token" in request.headers:
                token = request.headers['x-access-token']
                token_verification = verify_session_token(token)
                LOG.debug("TOKEN FOUND. is valid?: %s" %token_verification)

        return f(*args, **kwargs)
    return decorator

# API Authentication decorator
def API_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if TOKEN_REQUIERD:

            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']

            if not token: # throw error if no token provided
                return make_response(jsonify({"message": "A valid token is missing!"}), 401)
            try:

                if verify_API_KEY(token):
                    pass
                else:
                    return make_response(jsonify({"message": "Token invalid!."}), 401)
            except:
                return make_response(jsonify({"message": "Invalid token!"}), 401)

        else:
            if "x-access-token" in request.headers:
                token = request.headers['x-access-token']
                token_verification = verify_session_token(token)
                LOG.debug("TOKEN FOUND. is valid?: %s" %token_verification)

        return f(*args, **kwargs)
    return decorator





def login_request(username,password):
    url = 'http://%s/auth/v1/users/' % IP_AUTH_SERVICE
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    ToSend = {
        "option": "LOGIN",
        "user": username,
        "password": password
        }

    result = api.post(url, data=json.dumps(ToSend),headers=headers)
    if result.status_code==200:
        #registrar session
        json_result =result.json()
        expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=interval_expiration)
        LOG.info("la sesión expira en %s" %expiration_date)
        SESSIONS[json_result['data']['access_token']] = {"expiration_date":expiration_date, "tokenuser":json_result['data']['tokenuser']}
    return make_response(jsonify(result.json()), result.status_code)

def logout_request(tokenuser,access_token):
    try:
        update_access_token(access_token,tokenuser)
        return make_response(jsonify({"message": "Session closed", "status":"OK"}), 200)
    except:
        return make_response(jsonify({"message": "Invalid token!"}), 403)
    
def register_user(username,email,password):

    url = 'http://%s/auth/v1/users/' % IP_AUTH_SERVICE
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    ToSend = {
        "option": "NEW",
        "username": username,
        "email": email,
        "password": password,
        "tokenorg": TOKEN_ORG
        }

    result = api.post(url, data=json.dumps(ToSend),headers=headers)
    return make_response(jsonify(result.json()), result.status_code)


def verify_API_KEY(api_key):
    if api_key in SESSIONS:
        if "API_key" in SESSIONS[api_key]:
            LOG.debug("API KEY USED ...")
            return True

def verify_session_token(token):
    if token not in SESSIONS:
        return False
    else:
        if verify_API_KEY(token):
            return True
                
        expiration_date =SESSIONS[token]['expiration_date']
        tokenuser= SESSIONS[token]['tokenuser']

        now = datetime.datetime.now() 
        LOG.info("now: %s"% now)
        LOG.info("expire: %s"% expiration_date)
        LOG.info("expired?: %s"% (now>expiration_date))

        if now>expiration_date:
            update_access_token(token,tokenuser) #update token
            return False
        else:
            return True

def update_access_token(accesstoken,tokenuser):

    url = 'http://%s/auth/v1/users?access_token=%s' % (IP_AUTH_SERVICE,accesstoken)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    ToSend = {
        "option": "CHANGETOKEN",
        "tokenuser": tokenuser    
        }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = api.post(url, data=json.dumps(ToSend),headers=headers)
    LOG.debug(result.json())
    del SESSIONS[accesstoken]
    return True

def getUserBy_access_token(access_token):
    url = 'http://%s/auth/v1/user?access_token=%s' % (IP_AUTH_SERVICE,access_token)
    result = api.get(url).json()
    LOG.debug(result)
    tokenuser = None
    if 'data' in result:
        tokenuser = result['data']['tokenuser']
    return tokenuser