import configparser
import os

def ReadConfig():
    configpath = os.getenv('CONFIGPATH') #read url
    cfg = configparser.ConfigParser()
    cfg.read(configpath +"config.ini")
    return cfg