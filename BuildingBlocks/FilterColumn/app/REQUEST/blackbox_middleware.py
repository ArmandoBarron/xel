import sys,json
import pandas as pd
import os
from random import randint
import logging #logger
from base64 import b64encode,b64decode
import importlib
from . import Trigger
import tempfile


########## GLOBAL VARIABLES ###########
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
with open(ACTUAL_PATH+'AppConfig.json') as json_file:
    App_configurations = json.load(json_file) #read all configurations for services

NAME_APPLICATION = App_configurations["NAME_APPLICATION"]
INPUT_DATA_FORMAT = App_configurations['INPUT_DATA_FORMAT']
logging.basicConfig(level=logging.INFO)
LOGER = logging.getLogger()


def blackbox(data,params):

    ###########################################################################
    ################################# EXTRACT #################################
    ###########################################################################
    
    # add reserverd params for the blackbox
    head, tail = os.path.split(data['data'])
    params['BBOX_INPUT_PATH']=head+"/" #input file created in S
    params['BBOX_INPUT_NAMEFILE']=tail  #input file created in S

    # intermediate PATH
    params['BBOX_TEMP_PATH']= tempfile.mkdtemp() +"/"
    # output path
    params['BBOX_OUTPUT_PATH']=tempfile.mkdtemp() +"/"
    # rollback path
    if not os.path.exists(ACTUAL_PATH+"rollback/"):
        try:
            os.makedirs(ACTUAL_PATH+"rollback/")
        except Exception as identifier:
            pass
    
    params['BBOX_ROLLBACK_PATH']=tempfile.mkdtemp(dir=ACTUAL_PATH+"rollback/") +"/"

    
    data_type= data['type']
    if data_type == "error":
        return {'data':'','type':'','status':'ERROR','message':"bad input. %s not supported by %s" % (data_type,NAME_APPLICATION)}
    if data_type in INPUT_DATA_FORMAT or "any" in INPUT_DATA_FORMAT: #if the app can manage the input
        LOGER.error("Input format is supported")
    else:
        return {'data':'','type':'','status':'ERROR','message':"bad input. %s not supported by %s" % (data_type,NAME_APPLICATION)}
    ######################################################################
    ############################## TRANSFORM #############################
    ######################################################################

    ####################### execute the application ######################
    response = Trigger.execute(params,App_configurations)
    LOGER.error("RESPONSE: %s" % response['status'])

    if response['status'] != 0:
        return {'data':'','type':'','status':'ERROR','message':"Bad execution in %s blackbox: %s" % (NAME_APPLICATION,response['data']['message'])}
    response = response['data']

    ######################################################################
    ################################ LOAD ################################
    ######################################################################
    
    #### verify if file not exist
    if os.path.isfile(response['data']):
        LOGER.warning("File with results was generated")
    else:
        LOGER.error("File with results not found")
        response = {'data':'','type':'','status':"ERROR","message":"OUTPUT FILE NOT FOUND IN %s " % NAME_APPLICATION }
        return response

    ### verify if is empty
    if os.stat(response['data']).st_size == 0:
        LOGER.error("File with results was generated, but its empty.")
        response = {'data':'','type':'','status':"ERROR","message":"OUTPUT FILE IS EMPTY %s " % NAME_APPLICATION }

    return response 

