#!/usr/bin/env python3.7

import json
#from Tools.Extract import ExtractData
from Tools.functions import Tools
from flask import Flask, request,jsonify,Response
from flask_api import status
import os
import logging #logger
from Tools.DB_handler import Handler
from flask_socketio import SocketIO,send, emit
from Tools.watcher import Centinel
from Tools.ReadConfigFile import ReadConfig
from Services.ServiceFacatory import ServiceFactory
from base64 import b64decode,b64encode

app = Flask(__name__)
socketio = SocketIO(app)

########################## Global variables #########################

Log = logging.getLogger()
WORKSPACE = dict()
SERVICE = ReadConfig()
SERVICE = SERVICE['services']


centinel_status = os.getenv('CENTINEL') #read url
if centinel_status == "active":
    centinel_status = True
    CENTINEL  = Centinel()
else: 
    centinel_status = False
    CENTINEL = None
Log.warning("--------------------------------------------------------------")
Log.warning("SENTINEL STATUS: "+str(centinel_status))

####################################################################
############################# API INFO #############################
####################################################################

@app.route('/')
def info():
    version = "1.0"
    name = "Transversal Processing Services (TPS)"
    base_url = "http://localhost:54350/"
    author = "Juan Armando Barrón Lugo"
    licence = base_url+"licence"
    docs = base_url+"documentation"
    Services_aviable = { 
		"01":"TPS/describe",
		"02":"TPS/ANOVA"
    }
    index = {'version':version, 'name':name, 'author':author, 'licence':licence,
		'docs':docs, 'apiUrl':base_url, 'Services':Services_aviable}
    return jsonify(index)


####################################################################
############################## TOOLS ###############################
####################################################################

def Validate_Workspace(WS):
    global WORKSPACE
    if WS in WORKSPACE:
        return True
    else:
        WORKSPACE[WS] = Tools(WS,CENTINEL)
        return True

def Validate_DS(WS,ds_name):
    global WORKSPACE
    Validate_Workspace(WS)
    return WORKSPACE[WS].Exist_DS(ds_name)



#web socket

@socketio.on('status')
def handle_message(message):
    global CENTINEL
    try:
        """
        must be recived a message with
        'workflow,workflow_id,task,status'
        """
        workflow,workflow_id,task,status=message.split(",")

        if centinel_status:
            CENTINEL.updateRecords(workflow,task,status)
            CENTINEL.InsertWorkflow(workflow,workflow_id)

    except Exception as e:
        Log.error('received message: ' + str(e))
        send("MESSAGE WAS NOT CORRECT")


@socketio.on('workingdir')
def handle_workingdir(message):
    global CENTINEL
    try:
        """
        must be recived a message with
        'workflow,task,working_dir'
        """

        workflow,task,working_dir=message.split(",")

        if centinel_status:
            CENTINEL.InsertWD(workflow,task,working_dir)

    except Exception as e:
        Log.error('received message: ' + str(e))
        send("MESSAGE WAS NOT CORRECT")

@socketio.on('socketCheck')
def socket_check(message):
    global CENTINEL
    try:
        """
        check status centinel
        """
        send(centinel_status)
    except Exception as e:
        Log.error('received message: ' + str(e))


#-------------------------------------------check healty
@app.route('/check')
def check():
    return jsonify({"status": "ok"})

@app.route('/extract', methods=['PUT','POST'])
def ExtracDataFromDS():
    try:
        global WORKSPACE
        params = request.get_json()
        if 'Workspace' not in params and 'DS' not in params:
            raise KeyError("Client or DS not found in params")

        ws_name = params["Workspace"]
        ds = params["DS"]
        Validate_Workspace(ws_name)
        WORKSPACE[ws_name].initManager(ds)
        return jsonify({"status": "OK", "message": "Data source extracted and saved"}), status.HTTP_201_CREATED
    except KeyError as e:
            print("KEY ERROR"+str(e))
            return jsonify({"status": "error", "message": "Key error %s in json" % e}), status.HTTP_409_CONFLICT

#-------------------------------------------RETURN THE DATA FROM A GIVEN DATASOURCE
@app.route('/<workspace>/', methods=['GET'])
@app.route('/<workspace>/<datasource>/', methods=['GET'])
def get_DS_data(workspace,datasource="all",format="response",client = None):
    global WORKSPACE
    if datasource == "all":
        Validate_Workspace(workspace)
        print(workspace)
        data = WORKSPACE[workspace].Get_all()
    else:
        if Validate_DS(workspace,datasource): #if data source exist
            data = WORKSPACE[workspace].Get_DS(datasource)
        else:
            return jsonify({"status": "error", "message": "Datasource %s not found in workspace" % datasource}), status.HTTP_409_CONFLICT
    if format=="response":
        return jsonify(data)
    elif format == "string":
        return json.dumps(data, indent=4, sort_keys=True)
    else:
        return json.dumps(data, indent=4, sort_keys=True)

#-------------------------------------------PUT THE DATA FROM A GIVEN DATASOURCE
@app.route('/<workspace>/putdata/<datasource>/', methods=['POST','PUT'])
def put_DS_data(workspace,datasource,format="response",client = None):
    try:
        global WORKSPACE
        params = request.get_json()
        if 'data' not in params:
            raise KeyError("data not found in params")

        tar_data = b64decode(params["data"].encode())
        path = params["path"]

        Validate_Workspace(workspace)
        WORKSPACE[workspace].Extract_from_local(tar_data,path,datasource)
        return jsonify({"status": "OK", "message": "Data source extracted and saved"}), status.HTTP_201_CREATED
    except KeyError as e:
        print("KEY ERROR"+str(e))
        return jsonify({"status": "error", "message": "Key error %s in json" % e}), status.HTTP_409_CONFLICT

####################################################################
############################# SERVICES #############################
####################################################################


##-------------------------------------------DESCRIBE THE GIVEN DATASET WITH STATISTICAL FUNCTIONS
@app.route('/<workspace>/TPS/<tps>', methods=['POST'])
def TPS(workspace,tps):
    global WORKSPACE
    #input data is prepared

    jsondata = request.get_json()
    TPP_instructions = jsondata['query'] #all the instruction to get the data from the database
    params = jsondata["options"] #all the options for the callable service
    label = jsondata["label"] #name of the new TPS (if its none, nothing it will be saved)

    Validate_Workspace(workspace) #we create the workspace
    
    if 'workload' in jsondata: #workload could be an external dataset
        TPP = jsondata['workload'] #external data is loaded
    else:
        TPP = WORKSPACE[workspace].create_TPP(TPP_instructions) #create a dataset from the instruction
    try:
        if tps.lower()=="getdata": 
            if label is not None: #label option is for save result in DB
                WORKSPACE[workspace].Save_DS(TPP,label)
                return jsonify({"status":"Results saved as %s" % label})
            Log.error(TPP)
            return jsonify({'result':TPP})
        Factory = ServiceFactory()
        service = Factory.Instance(tps)
        if service is None: return jsonify({"status":"ERROR","message":"service not found"})
        TPP = service.format_data(TPP)
        response = service.request(TPP,params,SERVICE[tps])
        if label is not None: #label option is for save result in DB
            WORKSPACE[workspace].Save_DS(response['result'],label)
            return jsonify({"status":"Results saved as %s" % label})
        else:
            return response
    except KeyError as e:
        return jsonify({"status":"ERROR","message":"Key error: "+ str(e) + " Not in config.ini"})



if __name__ == '__main__':
    if centinel_status:
        socketio.run(app, host='0.0.0.0', port=5000,debug = True)
    else:
        app.run(host='0.0.0.0', port=5000,debug = True)

"""
        "Workspace": {
            "NAME": "Prueba",
            "DAGTP":"none"
        },
        "DS":[
            {
                "NAME": " ", 
                "TYPE": "FILE",
                "PATH": "conHeaders.csv",
                "HEADERS":"Antena,Fecha,Latitud,Longitud,Codigo,Temp_max_emas,Temp_min_emas,Humedad,Presion_barometrica,Precipitacion,Radiacion_solar"
            },

        ]
        """