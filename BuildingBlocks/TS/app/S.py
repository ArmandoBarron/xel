import sys,os,pandas,ast
from threading import Thread
from flask import request, url_for
from flask import Flask, request,jsonify,Response
import building_middleware as BB ##importing middleware
import json

BASE_PATH = os.getcwd()


app = Flask(__name__)
#root service
@app.route('/')
def prueba():
    return "Service Mersh"

#service to execute applications
@app.route('/execute', methods=['POST'])
def execute_service():
    os.chdir(BASE_PATH) #in case of error must be set the base path
    params = request.get_json()
    data = params['data'] #data to be transform
    actions = params['actions'] #dag
    service_params = params['params'] #parameters for the service
    result = BB.middleware(data,actions,service_params) #returns the result as json
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug = True)

