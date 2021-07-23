
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
    RESERVED_PARAMS={"SOURCE":params['BBOX_INPUT_PATH']+params['BBOX_INPUT_NAMEFILE'],"SINK":params['BBOX_OUTPUT_PATH'],"CWD":ACTUAL_PATH}

    Extract_config = AppConfig['EXTRACT']
    Transform_config = AppConfig['TRANSFORM']
    Load_config = AppConfig['LOAD']

    if Extract_config['COMPRESS']: #inputs are zip...
        utils.UncompressFile(RESERVED_PARAMS['SOURCE'],params['BBOX_TEMP_PATH'])
        RESERVED_PARAMS['SOURCE'] = params['BBOX_TEMP_PATH'] #now the folder is the source

    ############## develepores can modify this function in order to set the envirioment to the app ###########
    CustomScript.config_env()
    ##########################################################################################################

    try:

        ######################### call the application #########################
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
            command = utils.FormatCommand(command,params,reserved_params=RESERVED_PARAMS)
            execution_status = os.system(command)
        ########################################################################

        ### some assumtions###
        ### data results are in SINK (BBOX_OUTPUT_PATH)
        ### must especify compress option or output_namefile option... in other case a error will rise.

        if Load_config['OUTPUT_NAMEFILE'] !="":
            namefile = utils.FormatCommand(Load_config['OUTPUT_NAMEFILE'],params,reserved_params=RESERVED_PARAMS) #format namefile 
            if len(namefile.split("/"))>=2: #its a path
                result = namefile
            else:
                result=RESERVED_PARAMS['SINK']+namefile #its just a file name and we add a default path
            result = shutil.copy(result,params['BBOX_ROLLBACK_PATH']) #copy file generated to rollback folder

        if Load_config['COMPRESS']:
            result = utils.CompressFile(params['BBOX_ROLLBACK_PATH'],RESERVED_PARAMS['SINK'],ignore_list=Load_config['ignore_list'])

        #clean everything
        #shutil.rmtree(params['BBOX_INPUT_PATH'],ignore_errors=True)
        os.remove(params['BBOX_INPUT_PATH']+params['BBOX_INPUT_NAMEFILE'])
        shutil.rmtree(params['BBOX_TEMP_PATH'],ignore_errors=True)
        shutil.rmtree(params['BBOX_OUTPUT_PATH'],ignore_errors=True)

        name,ext = result.split(".")
        LOGER.error(result)
        response = {"data":result,"type":ext,"status":"OK","message":"OK"}

    except (Exception,ValueError) as e:
        LOGER.error("wooowoowoooo"+ str(e))
        response = {"data":"","type":"","status":"ERROR","message":""}
        response['message']=str(e)
        return {'status':1,'data':response}

    return {'status':execution_status,'data':response}