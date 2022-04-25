import sys,json
import pandas as pd
import os
from random import randint
import logging #logger
from base64 import b64encode,b64decode
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
LOGER = logging.getLogger()
from os.path import basename


def UncompressFile(path_compressfile,path_results):
    """
    path_compressfile::str -> /var/temp/file1.zip
    path_results::str -> /var/temp/
    """
    with ZipFile(path_compressfile, 'r') as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall(path_results)

def CompressFile(path_compressfile,path_results,ignore_list=[]):
    """
    path_compressfile::str -> /var/temp/file1.zip
    path_results::str -> /var/temp/
    """
    fname = path_compressfile+"output.zip"
    with ZipFile(fname, 'w') as zipObj:
    # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(path_results):
            for filename in filenames:
                #create complete filepath of file in directory
                if filename not in ignore_list:
                    filePath = os.path.join(folderName, filename)
                    archive_file_path = os.path.relpath(filePath, path_results)
                    # Add file to zip
                    zipObj.write(filePath, archive_file_path)
                    #zipObj.write(filePath, os.path.relpath(filePath, src_path))

    return fname

def FormatParam(param):
    if isinstance(param, list):
        return ",".join([str(i) for i in param])
    elif isinstance(param, dict):
        return json.dumps(param)
    else:
        return str(param)


def FormatCommand(command,params,reserved_params={}):
    
    while True:
        start = command.find('@{') + 2
        if start==1: #given that -1 + 2 = 1
            break
        end = command.find('}', start)
        if start>end:
            return None
        parameter_found = command[start:end]
        #LOGER.error("---------------> %s" % parameter_found)
        ########## REPLACE PARAMS FOUND #############
        if parameter_found in reserved_params:
            command = command.replace("@{%s}" % parameter_found,reserved_params[parameter_found])
        elif parameter_found in params:
            temp_p = FormatParam(params[parameter_found]) #fillter the params to change it to a valid format (e.g a list [] to a string separated by commas)
            command = command.replace("@{%s}" % parameter_found,temp_p)
        else:
            #if the parameter does not exist, then a default - is allocated
            command = command.replace("@{%s}" % parameter_found,"-")

    
    return command
