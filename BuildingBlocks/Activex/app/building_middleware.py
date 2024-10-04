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


## this is bassically the building block ##
ignore_list = ['TPS'] #list of folders to ignore 
list_applications = [name for name in os.listdir(".") if (os.path.isdir(name) and name not in ignore_list)]



def middleware(data,actions,workParams,LOGER=LOG,ENV={},POSTMAN = None):
    try:
        LOGER.info(list_applications)
        LOGER.info("Running BB middleware")
        BB_ST = time.time() #<--- time flag
        f = open(logs_folder+'Times.txt', 'a+') # times log
        
        C_ST = time.time() #<--- time flag
        if len(actions)<=0:
            LOGER.error("No APPs selected.")
            raise Exception("No APPs selected.")

        for app in actions:
            app = app.upper() #all applications names must be in uppercase
            LOGER.info("Looking for %s" % app)
            #confirm the app exist in BB, if not, do nothing
            if (app in list_applications):
                filepath = app + '/'

                #import module
                LOGER.debug("importing....."+ app+'.blackbox_middleware')
                mod = importlib.import_module(app+'.blackbox_middleware')
                
                #get params for service
                params = workParams[app] #it has the character for the application and _params (e.g. A)

                #ADD ENV params
                params['ENV'] = ENV

                #execute application as blackbox
                LOGER.info("RUNNING BLACKBOX")
                data = mod.blackbox(data,params,POSTMAN=POSTMAN) #data is a json
                LOGER.info("BLACKBOX FINISHED with status: %s" % data['status'])

                #write log
                f.write("%s, %s \n" %(app, (time.time() - C_ST))) #<--- time flag

                if data['status'] == "ERROR":
                    LOGER.error(">>> ERROR DETECTED <<< \n STOPING BB")
                    return data
                #the same data variable is transformed by all the application
            else:
                LOGER.error("APP %s doesn't exist in BB..." % app)
                raise Exception("App not found")

        LOGER.info("STOPING BB")
        f.write("BB, %s \n-\n" %((time.time() - C_ST))) #<--- time flag
        f.close() 
        return data #{data:,type}
    except Exception as ex: #catch everything
        f.write("BB, %s \n-\n" %((time.time() - C_ST))) #<--- time flag
        f.close() 
        LOGER.error("Unexpected error in BB middleware. %s" %(ex))
        return {'data':'','type':'','status':'ERROR','message':'Unexpected error in BB middleware. %s' %(ex)}