import logging
import logging.config
import os
from logging.config import fileConfig
import threading
from TPS.TPS_api import API as TPSapi
from requests.exceptions import ConnectionError

from time import time, sleep


class Builder(object):

    def __init__(self,workspace_name, json_dagtp_solution= None,TPS_manager_host = None):
        self.name = workspace_name
        self.running = False
        self.logger = logging.getLogger()

        self.DS = [] #list of DS 
        if json_dagtp_solution is not None:
            if 'Tasks' in json_dagtp_solution:
                self.dagtp = json_dagtp_solution
                self.running = True
            else: raise Exception("Incorrrect format in json_dagtp_solution")
        
        if TPS_manager_host is not None:
            self.TPSM = TPS_manager_host
        else:
            self.TPSM = os.getenv("TPS_MANAGER_HOST")
        
        try:
            self.TPSapi = TPSapi(self.TPSM,self.name)
            self.is_tpsapi_available = True
            self.logger.debug("TPS API is alive")
        except ConnectionError as e:
            self.logger.error(e)

    def TPS_data_extraction(self, task, workflow,monitor = "dagsink" , path= None,label = None):
        """
        Extracts data processed by a task and is saved into the TPS manager.
        task: name of the task
        path: additional path
        label: adding an name (or alias) to data extracted
        """
        if path is None: taskpath = task
        else: taskpath = task + ":/" + path

        if self.running == False: #the solution is not ready
            ds_formated = self.TPSapi.format_ds(task,"ID",monitor,workflow,ds_id=taskpath,watch=True,label=label)
        else:
            ds_formated = self.TPSapi.format_ds(task,"ID",self.dagtp,workflow,ds_id=taskpath,label=label)

        self.DS.append(ds_formated)


    def init_tps(self):
        """
        Initialize the TPS manager with the TPS created

        :raises Exception: when there is an error with the call
        """
        if self.is_tpsapi_available == True:
            jsondata = self.TPSapi.format_workspace(self.name,self.DS)
            self.TPSapi.LoadData(jsondata) #load DAGtps and tpp points to service
            self.logger.debug("TPS LOADED")

