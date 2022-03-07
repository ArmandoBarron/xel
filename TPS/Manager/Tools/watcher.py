import logging #logger
from time import time, sleep
import configparser
import asyncio
from Tools.ReadConfigFile import ReadConfig


class Watcher:

    def __init__(self,name):
        self.cfg = ReadConfig()
        self.Log = logging.getLogger()
        self.api_name= name
        self.api = None
        self.status = True
        try:
            if self.api_name == "dagon":
                from Tools.api.dagon_api import API as api
                self.api = api(self.cfg['watcher_apis']['dagon'])
            elif self.api_name == "dagsink":
                from Tools.api.Repository import API as api
                self.api = api(self.cfg['watcher_apis']['dagsink'])
            elif self.api_name == "decaf":
                pass
            else:
                raise ValueError("No api founded")

        except ConnectionError as e:
            self.Log.error(e)
            self.status = False
            raise ValueError("Api error")



    def wait_task(self,task_name,workflow_name):
        #wf_id = self.api.get_workflow_by_name(workflow_name)
        while(True):
            self.Log.warning("IM THE WATCHER")
            task = self.api.get_task(workflow_name,task_name)
            if task['task']['status'] == "FINISHED":
                break
            else:
                self.Log.info("waiting task %s, actual status: %s" %(task_name,task['status']) )
                sleep(1)

        return self.api.get_workflow(workflow_name)

class Centinel:

    def __init__(self):
        self.records = dict()
        self.registred_workflows = dict()
        self.Log = logging.getLogger()
        self.finish_status = ["FINISHED","OVER","END"] 

    
    def updateRecords(self,workflow,task,status):
        if not workflow in self.records: self.records[workflow]=dict()
        if not 'tasks' in self.records[workflow]: self.records[workflow]['tasks']=dict()
        if not task in self.records[workflow]['tasks']: self.records[workflow]['tasks'][task]=dict()
        self.records[workflow]['tasks'][task]['status'] = status 

    def InsertWorkflow(self,workflow,workflow_id):
        self.registred_workflows[workflow]=workflow_id

    def InsertWD(self,workflow,task,working_dir):
         self.records[workflow]['tasks'][task]['working_dir'] = working_dir 

    def getStatus(self,workflow,task):
        try:
            return self.records[workflow]['tasks'][task]['status']
        except KeyError as e:
            self.Log.warning("Record not found: "+ str(e))
            return None

    def getWorkingdir(self,workflow,task):
        try:
            return self.records[workflow]['tasks'][task]['working_dir']
        except KeyError as e:
            self.Log.warning("Record not found: "+ str(e))
            return None

    def workflow_as_json(self,workflow):
        return self.records[workflow]

    def getWorkflowID(self,workflow):
        try:
            return self.registred_workflows[workflow]
        except KeyError as e:
            self.Log.warning("Record not found: "+ str(e))
            return None

    def wait_task(self,task,workflow):
        try:
            while(True):
                self.Log.warning("CENTINEL waiting for task %s" % task )

                status = self.getStatus(workflow,task)
                working_dir = self.getWorkingdir(workflow,task)
                if status is not None and status in self.finish_status and working_dir is not None: break;
                sleep(1)
            
            return self.workflow_as_json(workflow)
        except KeyError as e:
            self.Log.warning("This is impossible: "+ str(e))
            return 1