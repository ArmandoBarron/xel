import json
import os
import logging #logger
import shutil

LOGER = logging.getLogger()

def config_env():
    pass

def custom_app(app_params,reserved_params):

    app_params['input_distance_filename'] = reserved_params['SOURCE'] +app_params['input_distance_filename']
    app_params['clustered_dataframe_filename'] = reserved_params['SOURCE'] +app_params['clustered_dataframe_filename']
    app_params['outputfile'] = reserved_params['SINK']+"representation.png"
    
    # call the application
    params = json.dumps(app_params)
    execution_status = os.system("python3 "+reserved_params['CWD']+"T.py '"+params+"'")

