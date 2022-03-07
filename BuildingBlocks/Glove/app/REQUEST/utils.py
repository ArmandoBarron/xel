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
                    # Add file to zip
                    zipObj.write(filePath, basename(filePath))
    return fname


def FormatCommand(command,params,reserved_params={}):
    
    while True:
        start = command.find('@{') + 2
        if start==1: #given that -1 + 2 = 1
            break
        end = command.find('}', start)
        if start>end:
            return None
        parameter_found = command[start:end]
        ########## REPLACE PARAMS FOUND #############
        if parameter_found in reserved_params:
            command = command.replace("@{%s}" % parameter_found,reserved_params[parameter_found])
        elif parameter_found in params:
            command = command.replace("@{%s}" % parameter_found,str(params[parameter_found]))
        else:
            command = command.replace("@{%s}" % parameter_found,"")

    
    return command
