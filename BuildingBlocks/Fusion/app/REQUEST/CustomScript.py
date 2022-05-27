import json
import os
import logging #logger
import shutil

def config_env():
    pass


def custom_app(app_params,reserved_params):

    #create the command
    list_files= app_params['list_files'] #string ;
    list_columns= app_params['list_columns'] #string ;
    method= app_params['method'] #string ;


    list_files = list_files.replace(", ",",").replace("; ", ";").split(",")
    list_columns = list_columns.replace(", ",",").replace("; ", ";").split(";")

    i=0
    command = "python %smerge.py \'" %(reserved_params["CWD"])
    #merge.py data/file1.csv:[column_name1.column_name2],data/file2.csv:[column_name3.column_name4] inner output/output.csv
    for fil in list_files:
        command+=  "%s%s:[%s];" %(reserved_params['SOURCE'],list_files[i], list_columns[i])
        i+=1

    command = command[:-1]
    command+= "\' %s %smerged.csv" %(method, reserved_params['SINK'])

    print(command)
    execution_status = os.system(command)
    return 0