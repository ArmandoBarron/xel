import sys,json
import pandas as pd
import os
from random import randint
import logging #logger

LOGER = logging.getLogger()

def execute(params):
    LOGER.error(params)
    """
    params:: type(dict)

    here is the only part must be modified
    in this file we asume that the application produce a single file
    use this space to return a pandas dataframe with the results
    """ 
    filepath = params['inputpath']
    filename = params['inputfile']+".csv"
    destination =  params['inputfile']+"_results.csv"
    columns = params['columns']
    method = params['method']
    os.system('Rscript T.r "'+filepath+'" "'+filename+'" "'+destination+'" "'+columns+'" "'+method+'"')


    data = pd.read_csv(destination)

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

    #write data on disk
    destination = input_folder + inputfile_name+".csv"
    data.to_csv(destination, index = False, header=True)

    ###############################################
    ################## TRANSFORM ####################
    ###############################################
    #execute the application
    data = execute(params)
    ###############################################
    ################## LOAD ####################
    ###############################################

    
    #return to the base path
    os.chdir(actual_path)
    return data    #data is a pandas dataframe
