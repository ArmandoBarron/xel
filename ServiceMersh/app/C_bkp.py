import socket
import sys
import pickle
import json
import requests as api #for APIs request

def RestRequest(ip,port,message):

        url = 'http://%s:%s/execute' %(ip,port) #calling the bb
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        result = api.post(url, data=json.dumps(message),headers=headers)
        RES = result.json()
        return RES
