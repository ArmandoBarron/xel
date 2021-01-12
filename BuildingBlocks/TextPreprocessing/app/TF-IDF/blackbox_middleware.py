import sys,json
import pandas as pd
import os
from random import randint
import logging #logger
from base64 import b64encode,b64decode

import importlib
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
from os.path import basename

NAME_APPLICATION = "TF-IDF"
INPUT_DATA_FORMAT = ["csv"]
OUTPUT_DATA_FORMAT = "zip"

LOGER = logging.getLogger()
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

def execute(params):
    
    """
    params:: type(dict)

    here is the only part must be modified
    in this file we asume that the application produce a single file
    use this space to return the results
    """ 


    params['inputfile'] = params['inputpath']+params['inputfile']+".csv"  #where the input data is (without the extension)
    params['matrix_outputfile'] = ACTUAL_PATH + 'tfidf_matrix.pkl'
    params['dist_outputfile'] = ACTUAL_PATH + 'dist.pkl'
    outputfile = params['inputpath']+params['outputfile']+"."+OUTPUT_DATA_FORMAT #where the output data must be4
    input_filename=  params['inputfile']
    LOGER.error(params)

    params = json.dumps(params)
    # call the application
    execution_status = os.system("python3 "+ACTUAL_PATH+"T.py '"+params+"'")
    
    # create a ZipFile object
    with ZipFile(outputfile, 'w') as zipObj:
        zipObj.write(ACTUAL_PATH+'tfidf_matrix.pkl', 'tfidf_matrix.pkl')
        zipObj.write(ACTUAL_PATH+'dist.pkl', 'dist.pkl')
        zipObj.write(input_filename, 'default.csv')


    #return status
    return {'status':execution_status,'data':''}


def blackbox(data,params):

    #its always an ETL. we dont need a dag
    #since the data its in variable data we need to write a file so T application can read it
    #the file is created with a random name to avoid confilc on parallel request.
    
    ###########################################################################
    ################################# EXTRACT #################################
    ###########################################################################
    data_type = data['type']

    input_folder= ACTUAL_PATH+"input_data/"
    try:
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)
    except FileExistsError:
        pass


    inputfile_name = "input_%s" % randint(1,1000)
    outputfile_name = "output_%s" % randint(1,1000)


    source = input_folder + inputfile_name+"."+data_type
    destination = input_folder + outputfile_name+"."+OUTPUT_DATA_FORMAT

    ########### write data on disk and keep it on memory ########### 
    #### if type is csv, the inputdata is in memory in the variable INPUT_DATA
    if data_type in INPUT_DATA_FORMAT: #if the app can manage the input
        LOGER.error("correct input format")
    else:
        return {'data':'','type':'','status':'ERROR','message':"bad input. %s not supported by %s" % (data_type,NAME_APPLICATION)}

    if data_type=="csv":
        input_data = pd.DataFrame.from_records(data['data']) #data is now a dataframe
        input_data.to_csv(source, index = False, header=True) #write DF to disk
    else:
        with open(source,"wb") as file:
            file.write(b64decode(data['data'].encode()))

    ######################################################################
    ######################## SPACE FOR DEVELOPERS ########################
    ######################################################################

    params['inputpath'] = input_folder #where the input data is
    params['inputfile'] = inputfile_name #name of the input data
    params['outputfile'] = outputfile_name #name of the input data

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
