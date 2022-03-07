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
    LOGER.error(reserved_params['SOURCE'])
    df = pd.read_csv(reserved_params['SOURCE'])
    data = json.loads(df.to_json(orient="records"))

    data= mod.call_tps(data,app_params) #tps result
    if app_params['service']=="ANOVA" or app_params['service']=="describe":
        with open(reserved_params['SINK']+'output.json', 'w') as f:
            json.dump(data, f)

    elif app_params['service']=="graphics":
        with open(reserved_params['SINK']+'output.png', 'wb') as f:
            f.write(data)
    else:
        df = pd.DataFrame.from_records(data)
        LOGER.error(df)
        df.to_csv(reserved_params['SINK']+'output.csv',index=False)