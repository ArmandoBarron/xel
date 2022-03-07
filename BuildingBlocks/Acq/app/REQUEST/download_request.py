import sys
import os
import time
import pandas as pd
from base64 import b64decode,b64encode
import json
import requests
import shutil
import urllib.request as request
from contextlib import closing

LOCAL_FILES = "./FILES/"

def download_file_from_google_drive(id, destination):
        URL = "https://docs.google.com/uc?export=download"

        session = requests.Session()

        response = session.get(URL, params = { 'id' : id }, stream = True)
        token = get_confirm_token(response)

        if token:
                params = { 'id' : id, 'confirm' : token }
                response = session.get(URL, params = params, stream = True)

        save_response_content(response, destination)    

def get_confirm_token(response):
        for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                        return value

        return None

def save_response_content(response, destination):
        CHUNK_SIZE = 32768
        with open(destination, "wb") as f:
                for chunk in response.iter_content(CHUNK_SIZE):
                        if chunk: # filter out keep-alive new chunks
                                f.write(chunk)



def download_file(DOWNLOAD_server,OUTPUT_PATH,NAMEFILE,EXT,URL="",ID_FILE="",USER="",PASS="" ):

        destination = OUTPUT_PATH+NAMEFILE+"."+EXT

        if DOWNLOAD_server =="URL" or DOWNLOAD_server == "HYDROSHARE":
                response = requests.get(URL, allow_redirects=True)
                save_response_content(response,destination)
        elif DOWNLOAD_server == "GOOGLE_DRIVE" and ID_FILE !="":
                download_file_from_google_drive(ID_FILE, destination)
        elif DOWNLOAD_server == "FTP":
                if USER != "" and PASS != "": final_url = "ftp://"+USER+":"+PASS+"@"+URL
                else: final_url = "ftp://"+URL
                with closing(request.urlopen(final_url)) as r:
                        with open(destination, 'wb') as f:
                                shutil.copyfileobj(r, f)
        elif DOWNLOAD_server == "BB_FILES":
                destination = LOCAL_FILES+NAMEFILE+"."+EXT
        else:
                return 1
        return 0

