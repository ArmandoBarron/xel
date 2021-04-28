import json
import os
import logging #logger
import shutil

def config_env():
    pass


def custom_app(app_params,reserved_params):

    app_params['inputfile'] = reserved_params['SOURCE'] #csv

    app_params['matrix_outputfile'] = reserved_params['SINK'] + 'tfidf_matrix.pkl'
    app_params['dist_outputfile'] = reserved_params['SINK']  + 'dist.pkl'
    shutil.copy(app_params['inputfile'], reserved_params['SINK']+"default.csv")

    params = json.dumps(app_params)
    # call the application
    execution_status = os.system("python3 "+reserved_params['CWD']+"T.py '"+params+"'")
    
