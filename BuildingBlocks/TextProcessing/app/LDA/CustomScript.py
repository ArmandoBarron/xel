import json
import os
import logging #logger
import shutil

def config_env():
    pass

def custom_app(app_params,reserved_params):

    app_params['inputfile'] = reserved_params['SOURCE']
    app_params['output_folder'] = reserved_params['SINK']

    params = json.dumps(app_params)
    execution_status = os.system("python3 "+reserved_params['CWD'] +"T.py '"+params+"'")
    
