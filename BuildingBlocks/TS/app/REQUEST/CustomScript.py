import json
import os
import logging #logger
import shutil
import importlib
import pandas as pd

LOGER = logging.getLogger()

def config_env():
    pass

def custom_app(app_params,reserved_params):
    mod = importlib.import_module('REQUEST.tps_request')
    #transform to json
    data = json.load(reserved_params['SOURCE'])
    LOGER.error(params)

    try:
        data= mod.call_tps(data,app_params) #tps result
        if app_params['service']=="ANOVA" or app_params['service']=="describe":
            with open(reserved_params['SINK']+'output.json', 'w') as f:
                json.dump(data, f)

        elif app_params['service']=="graphics":
            with open(reserved_params['SINK']+'output.png', 'wb') as f:
                json.dump(data, f)
        else:
            df = pd.Dataframe.from_records(data)
            df.to_csv(reserved_params['SINK']+'output.csv')