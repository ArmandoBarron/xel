import sys,os,json
import pandas as pd
import importlib
import logging #logger
LOG = logging.getLogger()

## this is bassicaly the building block ##

dictionary = {}
with open("building_structure.json", "r") as json_file:
    dictionary = json.load(json_file) #read all configurations for services


def middleware(data,DAG,workParams):
    """
    data its a dict with records
    """
    LOG.error("running BB")
    #data = pd.DataFrame.from_records(data) #data is now a dataframe

    for char in DAG:

        LOG.error(char)
        char = char.upper()
        DAG = DAG.replace(char,"",1)

        #get config for application
        appconfig = dictionary[char]
        filepath =appconfig['path'] + '/'
        resultname =appconfig['resultname'] #these are not used

        #import module
        LOG.error("importing....."+ appconfig['path']+'.blackbox_middleware')
        mod = importlib.import_module(appconfig['path']+'.blackbox_middleware')

        #exec("import %s.blackbox_middleware" % appconfig['path']) #e.g. import RNN.blackbox_middleware
        
        #get params for service
        params = workParams[char] #it has the character for the application and _params (e.g. A)

        #execute application as blackbox
        LOG.error("RUNNING BLACKBOX")
        data = mod.blackbox(data,params) #data is a json
        LOG.error("BLACKBOX FINISHED")
        LOG.error(data['status'])

        if data['status'] == "ERROR":
            LOG.error(" ERROR DETECTED ---- STOPING BB")
            return data

        #the same data variable is transformed by all the application
    
    LOG.error("STOPING BB")
    return data #{data:,type}