import sys,json
import pandas as pd
import os
from random import randint
import logging #logger
import importlib
#####
from base64 import b64encode


LOGER = logging.getLogger()

def execute(data,params):
    LOGER.error(params)
    #import libraries in this folder
    mod = importlib.import_module('REQUEST.tps_request')


    """
    params:: type(dict)

    here is the only part must be modified
    in this file we asume that the application produce a single file
    use this space to return a pandas dataframe with the results
    """ 
    #transform to json
    data = json.loads(data.to_json(orient='records'))

    data= mod.call_tps(data,params)
    try:
        data = pd.DataFrame.from_records(data)
    except TypeError:
        image_bin = b64encode(data)
        data = {'data':image_bin.decode("utf-8")} #if type error then its binary data

    return data


def blackbox(data,params):

    #its always an ETL. we dont need a dag
    #since the data its in variable data we need to write a file so T application can read it
    #the file is created with a random name to avoid confilc on parallel request.
    
    ###############################################
    ################## EXTRACT ####################
    ###############################################

    actual_path = os.getcwd()
    #change workinf dir to blackbox location
    os.chdir(os.path.dirname(__file__))

    input_folder= "input_data/"
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)


    inputfile_name = "input_%s" % randint(1,1000)
    params['inputpath'] = input_folder
    params['inputfile'] = inputfile_name


    ###############################################
    ################## TRANSFORM ####################
    ###############################################
    #execute the application
    data = execute(data,params)
    ###############################################
    ################## LOAD ####################
    ###############################################

    
    #return to the base path
    os.chdir(actual_path)
    return data    #data is a pandas dataframe
