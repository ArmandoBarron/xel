from TPS.Builder import Builder #TPS API BUILDER
import sys
import os
import time
import pandas as pd
from base64 import b64decode,b64encode
import json
WORKSPACENAME = "SERVICEMERSH"
TPSHOST ="http://tps_manager:5000"


def call_tps(data,params):
        metaworkflow=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST)
        serv = params['service']

        query = metaworkflow.TPSapi.format_single_query("nothing") #query
        res = metaworkflow.TPSapi.TPS(query,serv,workload=data,options=params)

        return res['result']

