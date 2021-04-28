import json
import os
import logging #logger


def config_env():
    ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

    ## create config file
    configfile = {
        "grobid_server": os.getenv("GROBID_URL"),
        "grobid_port": "8070",
        "batch_size": 1000,
        "sleep_time": 5,
        "coordinates": [ "persName", "figure", "ref", "biblStruct", "formula" ]
    }

    with open('%sclient/config.json' % ACTUAL_PATH, 'w') as f: #save config file
        json.dump(configfile, f)


def custom_app(app_params,reserved_params):
    pass