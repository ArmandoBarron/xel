import json
import os
import logging #logger

LOGER= logging.getLogger()

def config_env():
    pass

def custom_app(app_params,reserved_params):
    #filepath = params['inputpath']
    app_params['inputfile'] = reserved_params['SOURCE']
    app_params['outputfile']  = reserved_params['SINK']+"output.csv"
    params = json.dumps(app_params)
    execution_status = os.system("python3 "+ACTUAL_PATH+"T.py '"+params+"'")
    LOGER.error(">>>>>>>>>>>>>>>>>" + str(execution_status))