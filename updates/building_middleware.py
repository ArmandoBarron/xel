import sys,os,json
import pandas as pd
import importlib
import logging #logger
import time


LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

#create logs folder
logs_folder= "./logs/"
try:
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
except FileExistsError:
    pass


#fh = logging.FileHandler(logs_folder+'info.log')
#fh.setLevel(logging.DEBUG)
#LOG.addHandler(fh)
## this is bassicaly the building block ##

dictionary = {}
with open("building_structure.json", "r") as json_file:
    dictionary = json.load(json_file) #read all configurations for services


def middleware(data,DAG,workParams):
    try:
        LOG.info("running BB")
        BB_ST = time.time() #<--- time flag
        f = open(logs_folder+'Times.txt', 'a+') # times log
         
        for char in DAG:
            C_ST = time.time() #<--- time flag
            LOG.debug(char)
            char = char.upper()

            #get config for application
            appconfig = dictionary[char]
            filepath =appconfig['path'] + '/'

            #import module
            LOG.info("importing....."+ appconfig['path']+'.blackbox_middleware')
            mod = importlib.import_module(appconfig['path']+'.blackbox_middleware')
            
            #get params for service
            params = workParams[char] #it has the character for the application and _params (e.g. A)

            #execute application as blackbox
            LOG.error("RUNNING BLACKBOX")
            data = mod.blackbox(data,params) #data is a json
            LOG.error("BLACKBOX FINISHED")
            LOG.error(data['status'])

            f.write("%s, %s \n" %(char, (time.time() - C_ST))) #<--- time flag
            if data['status'] == "ERROR":
                LOG.error(" ERROR DETECTED ---- STOPING BB")
                return data
            #the same data variable is transformed by all the application

        LOG.error("STOPING BB")
        f.write("BB, %s \n" %((time.time() - C_ST))) #<--- time flag
        f.write("-\n") #<--- time flag
        f.close() 
        return data #{data:,type}
    except Exception as ex: #catch everything
        f.write("BB, %s \n" %((time.time() - C_ST))) #<--- time flag
        f.write("-\n") #<--- time flag
        f.close() 
        return {'data':'','type':'','status':'ERROR','message':'Unexpected error in BB middleware. '+str(ex)}