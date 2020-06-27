import sys,os,pandas,ast
from threading import Thread
from flask import request, url_for
from flask import Flask, request,jsonify,Response

import json
#not necessary to import dinamicaly C and
import C

with open('coordinator_structure.json') as json_file:
    dictionary = json.load(json_file) #read all configurations for services

#select distribution algorithm
if(dictionary['config']['Distribution_Type'] == "Round Robin"):
    from T_i import roundRobin as coordinate
elif(dictionary['config']['Distribution_Type'] == "Pseudorandom"):
    from T_i import pseudorandom as coordinate
elif(dictionary['config']['Distribution_Type'] == "Two Choice"):
    from T_i import twoChoice as coordinate



def readActions(actionsString):
    actions = actionsString.split(",")
    return actions

def formPMsg(data,p_DAG,destinationFolder,destinationFile,workParams):
    msg = data,destinationFolder,destinationFile,p_DAG,workParams
    return msg

def formDLMsg(data,dl_DAG,destinationFolder,destinationFile,filename,workParams):
    msg = data,destinationFolder,destinationFile,dl_DAG,filename,workParams
    return msg


app = Flask(__name__)
#root service
@app.route('/')
def prueba():
    return "Service Mersh"

#service to execute applications
@app.route('/execute/<service>', methods=['POST'])
def execute_service(service):
    params = request.get_json()
    data = params['data'] #data to be transform
    service_params = params['params'] #parameters for the service
    if 'actions' in params:
        actions=params['actions'] #for the geoportal we just gona use a single set of actions
    else:
        actions = ['A'] #default exec the first service called A
        service_params = {'A':service_params}
    
    info_service = dictionary['services'][service] #get all the configurations from an specific service

    coordinator = coordinate(len(info_service['resources']),actions) #select the resource
    print(coordinator)
    
    list_resources = info_service['resources'] #list of dictionaries

    for package in coordinator:
        p_DAG = actions[package] #dag of applications
        res = list_resources[coordinator[package]]
        ip = res['ip']
        port = res['port']

        #send message to BB
        # folder is always ./ so its not necessary to add as a parameter
        msg = {
            'data':data,
            'actions':p_DAG,
            'params':service_params
            }

        data = C.RestRequest(ip,port,msg)
    return json.dumps(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555,debug = True)
    #ssl_context=('Certificados/cert.pem', 'Certificados/key.pem')
