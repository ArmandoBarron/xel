import json
import os
import logging #logger
import shutil

def config_env():
    pass


def custom_app(app_params,reserved_params):

    app_params['representation_filename'] = reserved_params['SOURCE']+app_params['representation_filename']
    app_params['input_frame_filename'] =reserved_params['SOURCE']+app_params['input_frame_filename']
    app_params['output_folder'] = reserved_params['SINK']
    app_params['model_output'] = reserved_params['SINK'] +'model.pkl'
    app_params['frame_output'] = reserved_params['SINK'] +'frame.csv'
    app_params['dist_output'] = reserved_params['SINK'] +'dist.pkl'
    shutil.move(reserved_params['SOURCE']+"dist.pkl",app_params['dist_output'])
    # call the application
    params = json.dumps(app_params)
    execution_status = os.system("python3 "+reserved_params['CWD']+"T.py '"+params+"'")
