import json
import os
import logging #logger


def config_env():
    pass

def custom_app(app_params,reserved_params):
            
    app_params['input_distance_filename'] = reserved_params['SOURCE'] +app_params['input_distance_filename']
    app_params['input_frame_filename'] = reserved_params['SOURCE']  +app_params['input_frame_filename']
    app_params['output_folder'] = reserved_params['SINK'] 
    
    # call the application
    params = json.dumps(app_params)
    execution_status = os.system("python3 "+reserved_params['CWD'] +"T.py '"+params+"'")
