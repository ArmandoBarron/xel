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
import time
import csv

def UncompressFile(path_compressfile,path_results):
    """
    path_compressfile::str -> /var/temp/file1.zip
    path_results::str -> /var/temp/
    """
    with ZipFile(path_compressfile, 'r',ZIP_DEFLATED) as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall(path_results)

def CompressFile(path_compressfile,path_results,ignore_list=[]):
    """
    path_compressfile::str -> /var/temp/file1.zip
    path_results::str -> /var/temp/
    """
    fname = path_compressfile+"output.zip"
    with ZipFile(fname, 'w', ZIP_DEFLATED) as zipObj:
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


def Get_Env_FromFile(archivo_csv):
    try:
        with open(archivo_csv, "r", newline="",encoding="utf-8-sig") as csv_file:
            csv_reader = csv.reader(csv_file)
            # Ignorar la primera línea (encabezados)
            encabezados = next(csv_reader)
            segunda_fila = next(csv_reader)
            segunda_fila_dict = dict(zip(encabezados, segunda_fila))
            json_data = json.dumps(segunda_fila_dict)
        
        return json.loads(json_data)
    except (FileNotFoundError, csv.Error) as e:
        return {}


def get_var_in_string(command,initial="$ENV"):
    start = command.find(initial+"(") + (1 + len(initial))
    if start==1: #given that -1 + 2 = 1
        return None
    end = command.find(')', start)
    if start>end:
        return None
    parameter_found = command[start:end]
    return parameter_found

def FormatCommand(command,params,reserved_params={},POSTMAN=None,default_none=True):
    """
    @{param}
    @{param::str::defult value}
    @{$ENV()}
    @{$VAR()}
    @{$REF::tabla.query} e.g. @{$REF.incidencias_mundial.}

    @{$VAR::descripcion.pez}

    """
    while True:
        #LOGER.error("command: %s" % command)
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

        elif "$REF" in parameter_found:
            # REF::mortality

            temporal_parm_found  = parameter_found.split("::",1)[1]

            if POSTMAN is not None:
                LOGER.info("si hay postman")
                if len(reserved_params['ENV_DATASET'])>=1:
                    LOGER.info("Enviando ENV DATASET: %s" %(reserved_params['ENV_DATASET']))
                    temp_p =POSTMAN.GetReference(temporal_parm_found,ENV=reserved_params['ENV_DATASET'])
                else:
                    temp_p =POSTMAN.GetReference(temporal_parm_found,ENV=params['ENV'])

                LOGER.info("resultado de postman: %s" %temp_p)
                command = command.replace("@{$REF::%s}" % temporal_parm_found,str(temp_p))
            else:
                LOGER.error("POSTMAN IS NONE") 
                command = command.replace("@{%s}" % parameter_found,"-")
                
        elif "$ENV" in parameter_found:
            temporal_parm_found  = get_var_in_string(parameter_found,initial="$ENV") #
            #LOGER.error("IMPRIMIENTO LA LISTA DE PARAMETROS:")
            #LOGER.error(params)
            #LOGER.error(params['ENV'])
            #LOGER.error("parametro encontrado en ENV:" +temporal_parm_found)

            if temporal_parm_found in params['ENV']:
                temp_p = FormatParam(params['ENV'][temporal_parm_found]) #fillter the params to change it to a valid format (e.g a list [] to a string separated by commas)
                command = command.replace("@{%s}" % parameter_found,temp_p)
            elif temporal_parm_found in reserved_params['ENV_DATASET']:
                temp_p = FormatParam(reserved_params['ENV_DATASET'][temporal_parm_found]) #fillter the params to change it to a valid format (e.g a list [] to a string separated by commas)
                command = command.replace("@{%s}" % parameter_found,temp_p)
            else:
                command = command.replace("@{%s}" % parameter_found,"NONE")

        else:
            #if the parameter does not exist, then a default - is allocated
            if default_none:
                command = command.replace("@{%s}" % parameter_found,"-")
            else:
                command = command.replace("@{%s}" % parameter_found,"")

    #LOGER.error("final command: %s" % command)
    return command
