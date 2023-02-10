
import sys,json
import pandas as pd
import os
from random import randint
import logging #logger
import importlib
from . import utils
from . import CustomScript
import shutil
import tempfile
import time
import subprocess
import multiprocessing as mp
import signal

ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
LOGER = logging.getLogger()

#############################
def execute(params,AppConfig):
    """
    params:: type(dict) - 
    AppConfig:: type(dict) 

    This space can be used by the developer to customize the execution, as well as specify any preprocessing prior to the execution of the application. 
    For this, the developer can use the following parameters as support:

    AppConfig: a dict with the params defined in AppConfig.json
    params: dict with the params sent by the user to the mesh. e.g. params['k'], params['potato']...
        it also has some reserved params:

            params['BBOX_INPUT_PATH']:: type(string). path of the inputfile. e.g. /var/temp/
            params['BBOX_INPUT_NAMEFILE']:: type(string). name of the inputfile e.g. dsadfgv.zip

            params['BBOX_TEMP_PATH']:: type(string). temporal path. e.g. /var/temp/temporaldir/

            params['BBOX_OUTPUT_PATH']:: type(string). path for output data.

            params['BBOX_ROLLBACK_PATH']:: type(string). Persistent folder for .

        
    return: dict(). {status,data:{'status','data','type','message'}}
    """ 
    RESERVED_PARAMS={"SOURCE":params['BBOX_INPUT_PATH']+params['BBOX_INPUT_NAMEFILE'],
                    "SOURCE_PATH":params['BBOX_INPUT_PATH'],
                    "SOURCE_FILENAME":params['BBOX_INPUT_NAMEFILE'],
                    "SINK":params['BBOX_OUTPUT_PATH'],
                    "CWD":ACTUAL_PATH}

    Extract_config = AppConfig['EXTRACT']
    Transform_config = AppConfig['TRANSFORM']
    Load_config = AppConfig['LOAD']

    if Extract_config['COMPRESS']: #inputs are zip...
        utils.UncompressFile(RESERVED_PARAMS['SOURCE'],params['BBOX_TEMP_PATH'])
        RESERVED_PARAMS['SOURCE'] = params['BBOX_TEMP_PATH'] #now the folder is the source
        #LOGER.error(os.listdir(RESERVED_PARAMS['SOURCE']))
        #LOGER.error(RESERVED_PARAMS['SOURCE'])

    ############## develepores can modify this function in order to set the envirioment to the app ###########
    CustomScript.config_env()
    ##########################################################################################################
    execution_status=1
    try:
        app_message="OK"
        ######################### call the application #########################
        EXECUTION_TIME = time.time()
        if Transform_config['CUSTOM_APP']:
            try:
                CustomScript.custom_app(params,RESERVED_PARAMS)
                execution_status=0
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                filename_error = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                LOGER.error("CUSTOMAPP ERROR: "+str(e)+", line: "+str(line_number)+ " in "+filename_error)
                execution_status=1
        else:
            command = Transform_config['COMMAND']
            #LOGER.error("==== FORMATING COMMAND ======")
            command = utils.FormatCommand(command,params,reserved_params=RESERVED_PARAMS)
            LOGER.error("==== EXECUTING COMMAND ====== %s" % command )
            results={"execution_status":0}
            def call_app(comando):
                sp = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True,close_fds=True)
                LOGER.error("==== PID ====== %s" % sp.pid )

                #sp.wait()
                try:
                    stdouterr, _ = sp.communicate(timeout=10000)
                    #stdouterr = stdouterr.decode("utf-8")
                    LOGER.error("==== EXECUTING COMPLETE ====== %s" % comando )
                    #logging.error(stdouterr)
                    #execution_status = sp.returncode
                    results["execution_status"] = sp.returncode
                    sp.stdout.close()
                    sp.terminate()
                except TimeoutError as te:
                    LOGER.error("==== TIMEOUT ====== %s" % comando )
                    sp.kill()
                    results["execution_status"] = 1
                return True

            thread1 = mp.Process(target = call_app, args = (command,) )
            thread1.start()
            thread1.join()
            thread1.terminate()
            thread1.close()

            execution_status = results["execution_status"]

            #execution_status = os.system(command)
        EXECUTION_TIME = time.time() - EXECUTION_TIME
        ########################################################################

        if (execution_status!=0):
            app_message="Internal error in the application"


        ### some assumtions###
        ### data results are in SINK (BBOX_OUTPUT_PATH)
        ### must especify compress option or output_namefile option... in other case a error will rise.

        if Load_config['OUTPUT_NAMEFILE'] !="":
            list_namefiles =  Load_config['OUTPUT_NAMEFILE'].split(",")
            if type(list_namefiles) is not list:
                list_namefiles = [Load_config['OUTPUT_NAMEFILE']]

            for tmp_name in list_namefiles: #check all posible outputs
                try:
                    namefile = utils.FormatCommand(tmp_name,params,reserved_params=RESERVED_PARAMS) #format namefile 
                    if len(namefile.split("/"))>=2: #its a path
                        result = namefile
                        #if its a path by default compress is TRUE
                        Load_config['COMPRESS']=True
                    else:
                        result=RESERVED_PARAMS['SINK']+namefile #its just a file name and we add a default path
                    result = shutil.copy(result,params['BBOX_ROLLBACK_PATH']) #copy file generated to rollback folder
                    break
                except Exception as e:
                    LOGER.error("-- NOT THIS ONE:%s" % tmp_name)
                    pass


        if Load_config['COMPRESS']:
            result = utils.CompressFile(params['BBOX_ROLLBACK_PATH'],RESERVED_PARAMS['SINK'],ignore_list=Load_config['ignore_list'])

        #clean everything
        #shutil.rmtree(params['BBOX_INPUT_PATH'],ignore_errors=True)
        
        os.remove(params['BBOX_INPUT_PATH']+params['BBOX_INPUT_NAMEFILE'])
        shutil.rmtree(params['BBOX_TEMP_PATH'],ignore_errors=True) #esto remueve los datos de entrada
        shutil.rmtree(params['BBOX_OUTPUT_PATH'],ignore_errors=True)
        
        name,ext = result.split(".")
        LOGER.error(result)
        response = {"data":result,"type":ext,"status":"OK","message":app_message,"EXECUTION_TIME":EXECUTION_TIME}

    except (Exception,ValueError) as e:
        response = {"data":"","type":"","status":"ERROR","message":"%s" %(e)}
        return {'status':1,'data':response}

    return {'status':execution_status,'data':response}