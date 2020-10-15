import sys,json
import pandas as pd
import os
from random import randint
import logging #logger
from base64 import b64encode,b64decode

import importlib


NAME_APPLICATION = "Acquisition"
INPUT_DATA_FORMAT = []
OUTPUT_DATA_FORMAT = "csv"

LOGER = logging.getLogger()
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"


def execute(params):
    #import libraries in this folder
    mod = importlib.import_module('REQUEST.download_request')

    """
    params:: type(dict)

    here is the only part must be modified
    in this file we asume that the application produce a single file
    use this space to return a pandas dataframe with the results
    """ 

    try:
        st= mod.download_file(params['DOWNLOAD_server'],
                                params['OUTPUT_PATH'],
                                params['NAMEFILE'],
                                params['EXT'],
                                params['URL'],
                                params['ID_FILE'],
                                params['USER'],
                                params['PASS']) # result
    except (Exception,ValueError) as e:
        LOGER.error(str(e))
        return {'status':0,'data':{"data":"","type":"","status":"ERROR","message":str(e)}}

    return {'status':st,'data':''}


def blackbox(data,params):

    #its always an ETL. we dont need a dag
    #since the data its in variable data we need to write a file so T application can read it
    #the file is created with a random name to avoid confilc on parallel request.
    
    ###########################################################################
    ################################# EXTRACT #################################
    ###########################################################################

    input_folder= ACTUAL_PATH+"input_data/"
    try:
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)
    except FileExistsError:
        pass


    outputfile_name = "output_%s" % randint(1,1000)

    destination = input_folder + params['NAMEFILE']+"."+params['EXT']

    ######################################################################
    ######################## SPACE FOR DEVELOPERS ########################
    ######################################################################

    params['OUTPUT_PATH'] = input_folder #where the input data is
    OUTPUT_DATA_FORMAT = params['EXT']
                ################## TRANSFORM ####################
                            #execute the application
    output_status = execute(params)

    if output_status['status'] != 0:
        return {'data':'','type':'','status':'ERROR','message':"Bad execution in %s. Check the parameters and input data. Hint: Maybe the \
            input data is dirty (e.g Strings in numerical columns, Null values, etc.)" % NAME_APPLICATION}

    if output_status['data'] != '':
        return output_status['data'] 

    ######################################################################
    ################################ LOAD ################################
    ######################################################################
    try:
        if OUTPUT_DATA_FORMAT=="csv":
            df_table = pd.read_csv(destination)
            output_data = {'data':json.loads(df_table.to_json(orient='records')),'type':OUTPUT_DATA_FORMAT,'status':"OK","message":"OK"}
        else:
            with open(destination,"rb") as file:
                    output_data = {'data':b64encode(file.read()).decode(),'type':OUTPUT_DATA_FORMAT,'status':"OK","message":"OK"}
    except FileNotFoundError:
        LOGER.error("OUTPUT FILE NOT FOUND IN %s " % NAME_APPLICATION )
        output_data = {'data':'','type':OUTPUT_DATA_FORMAT,'status':"ERROR","message":"OUTPUT FILE NOT FOUND IN %s " % NAME_APPLICATION }

    return output_data    #data is a json

