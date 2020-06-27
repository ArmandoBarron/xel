import pandas as pd
import json
import glob
import logging #logger
import os
from os import path
from Tools.ftp_publisher import FTP_API
#test
#CONFIGPATH= "/home/robot/Escritorio/Projects/TESIS/TEST/"
#SCHEMAPATH= "/home/robot/Escritorio/Projects/TESIS/TEST/"
CONFIGPATH= os.getenv('CONFIGPATH') 
SCHEMAPATH= os.getenv('SCHEMAPATH')

try:
    os.stat(SCHEMAPATH)
except:
    os.mkdir(SCHEMAPATH)       


EXTETIONS_SUPPORTED = ["txt","csv","json","TIF","jpg","png","c","py","xls"]

Log = logging.getLogger()
try:
    DAGtps = json.load(open(CONFIGPATH+"DAG_tps.json"))
except Exception as e:
    Log.warning("DAG_tps.json not fond: "+ str(e))

def ExtractData(DS, dagtps = None):
    if dagtps is not None:
        global DAGtps
        DAGtps = dagtps
    data=[]
    option = DS["TYPE"]
    if option == "FILE":
        data = fromFILE(DS)
    elif option == "DB":
        pass
    elif option == "ID":
        data = fromID(DS)
    elif option == "FOLDER":
        data = fromFOLDER(DS)
    
    return data


def CreateHeaders(arr):
    h =[]; i=1
    for a in arr:
        h.append("V"+str(i))
        i+=1
    return h

def fromID(DS):
    if 'HEADERS' in DS: headers = DS['HEADERS']
    else: headers="yes"
    ID= DS['ID'].split(':/') 
    host = DAGtps['host']
    workdir = DAGtps['tasks'][ID[0]]['working_dir']
    ds_folder = workdir.split('/')[-1] #return the las element. this is the folder where it is the data
    workdir = SCHEMAPATH+ds_folder+"/"
    
    #here we check if the folder exist, if not, we call the FTP api to get it from the external source
    #if not path.exists(workdir):
    ftp = FTP_API(host)
    #    ftp.downloadFiles(ds_folder,workdir) #we get the data from the FTP ip. the data is downloades into the schemafolder
    
    if len(ID) >1: #additional path
        addpath = ID[1] 
        temp = addpath.split(".") #if there is a file, this will generate at least an array of size 2

        if temp[-1] in EXTETIONS_SUPPORTED: 
            #workdir=workdir+ID[1]

            filetodownload = ID[1].split("/")[-1]
            extrapath = ID[1].replace(filetodownload,"")
            workdir= workdir+extrapath
            ftp.downloadFiles(ds_folder+extrapath,workdir,file_to_downlaod=filetodownload) #just to download a single file
            workdir= workdir+filetodownload #finally we add the file to the path

            data = ReadFile(workdir,headers=headers)
        else: 
            Log.error("-------------"+ds_folder)
            Log.error("-------------"+workdir)

            ftp.downloadFiles(ds_folder,workdir)
            workdir=workdir+ID[1]+'/'
            data = ReadFolder(workdir,headers=headers)
    else:
        data = ReadFolder(workdir,headers=headers)

    return data


def fromFILE(DS):
    pathfile =DS["PATH"]
    headers = DS["HEADERS"]
    return ReadFile(SCHEMAPATH+pathfile, headers=headers)


def fromFOLDER(DS):
    #only CSV is supported
    try:
        pathfile =SCHEMAPATH+DS["PATH"]
        headers = DS["HEADERS"]
        return ReadFolder(pathfile,headers=headers)
    except ValueError as e:
        Log.error("ERROR: Data not found,  "+ str(e))
        return None

def ReadFolder(workdir, headers = "no",extension="csv"):
    all_filenames = [i for i in glob.glob(workdir+'*.*')]
    Log.error(all_filenames)
    Log.error(workdir)

    #combine all files in the list
    try:
        combined_csv = pd.concat([pd.read_csv(f) for f in all_filenames ])
    except ValueError:
        concat_list= [pd.read_excel(f,converters={'FECHA': str}) for f in all_filenames]
        combined_csv = pd.concat(concat_list)

    #export to csv
    #combined_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')
    if headers == "yes": #getting headers
        pass
    elif headers=="no":
        fieldnames = CreateHeaders(combined_csv)
        combined_csv.columns =fieldnames
    else:
        combined_csv.columns =headers.split(",")
    data = combined_csv.to_json(orient='records')
    data = json.loads(data)
    return data

def ReadFile(path, headers="no"):
    pathfile = path

    ext = pathfile.split('.')[-1]  # file extention
    try:
        ext = ext.lower()
        if ext == "csv": # CSV FILE
            if headers == "yes": #getting headers
                data = pd.read_csv(pathfile)
            elif headers=="no":
                  data =pd.read_csv(pathfile,header=None)
                  fieldnames = CreateHeaders(data)
                  data.columns =fieldnames
            else:
                data =pd.read_csv(pathfile)
                data.columns =headers.split(",")
            data = data.to_json(orient='records')
            data = json.loads(data)
        elif ext in ['json']: #json file
            with open(pathfile, "r") as read_file:
                data = json.load(read_file)
        else:
            Log.error("It was not possible to open that kind of file ."+ext)
            Log.error("FILE WILL BE READ AS A BINARY FILE")
            with open(pathfile, mode='rb') as file: # b is important -> binary
                data = file.read()
    except (FileNotFoundError,ValueError) as identifier:
        Log.error("Something was wrong. Cause: "+ str(identifier))
        Log.error("FILE WILL BE READ AS A BINARY FILE")
        with open(pathfile, mode='rb') as file: # b is important -> binary
            data = file.read()
    return data