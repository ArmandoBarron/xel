import sys,json
import pandas as pd
import os
from random import randint
import logging #logger

LOGER = logging.getLogger()
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

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
    trainSize = params['trainSize']
    classColumn = params['classColumn']
    epoch = params['epoch']
    lossFunction = params['lossFunction']
    metric = params['metric']
    os.system('Rscript '+ACTUAL_PATH+'T.r "'+filepath+'" "'
                             +filename+'" "'
                             +destination+'" "'
                             +columns+'" "'
                             +trainSize+'" "'
                             +classColumn+'" "'
                             +epoch+'" "'
                             +lossFunction+'" "'
                             +metric+'"')


    data = pd.read_csv(destination)

    return data


def blackbox(data,params):

    #its always an ETL. we dont need a dag
    #since the data its in variable data we need to write a file so T application can read it
    #the file is created with a random name to avoid confilc on parallel request.
    
    ###############################################
    ################## EXTRACT ####################
    ###############################################

    input_folder= ACTUAL_PATH+"input_data/"
    try:
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)
    except FileExistsError:
        pass


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

    return data    #data is a pandas dataframe
