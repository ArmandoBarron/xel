import sys
import os
import time
import pandas as pd
import json

import logging #logger
logging.basicConfig(level=logging.INFO)
LOGER = logging.getLogger()

def FormatCommand(command):

        while True:
                start = command.find("{") + 1
                if start==0: #given that -1 + 1 = 0
                        break
                end = command.find("}", start)
                if start>end:
                        return None
                parameter_found = command[start:end]

                ########## REPLACE PARAMS FOUND #############
                command = command.replace("{%s}" % (parameter_found),"@DF_data['%s']" % parameter_found)
        return command


data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path

query_list= sys.argv[3].split(";") #query to process separated by;

query_filt_list= sys.argv[4].split(";") #query to process separated by;

DF_data = pd.read_csv(data_path)



# ==============================================================
for q in query_list:
        q = FormatCommand(q)
        LOGER.info(q)
        if q != "":
                DF_data = DF_data.eval(q)

for q in query_filt_list:
        q = FormatCommand(q)
        LOGER.info(q)
        if q != "":
                DF_data = DF_data.query(q)

DF_data.to_csv(output_path,index=False)

#print(DF_data)


