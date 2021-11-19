from threading import Thread
import time
import requests as api #for APIs request
import logging
import json
from TPS.Builder import Builder #TPS API BUILDER

class postman(Thread):

    def __init__(self,GATEWAYS_LIST,SERVICE,SERVICE_IP,SERVICE_PORT,NETWORK,TPSHOST,API_GATEWAY=None,LOGER=None):
        super(postman, self).__init__()
        if LOGER is None:
            self.LOGER = logging.getLogger()
        else:
            self.LOGER=LOGER

        ####
        self.API_GATEWAY=API_GATEWAY
        self.GATEWAYS_LIST=GATEWAYS_LIST
        self.SERVICE=SERVICE
        self.SERVICE_IP=SERVICE_IP
        self.SERVICE_PORT=SERVICE_PORT
        self.NETWORK=NETWORK
        self.TPSHOST=TPSHOST
        ##################
        self.status = "STANDBY"
        self.RN=None
        self.id_service = None
        self.last_message ={}
        self._running=True


    def init_service(self):
        try:
            if self.SERVICE is not None and self.SERVICE_IP is not None and self.SERVICE_PORT is not None:
                ToSend=json.dumps({"SERVICE":self.SERVICE,"IP":self.SERVICE_IP,"PORT":int(self.SERVICE_PORT),"NETWORK":self.NETWORK})
                url = 'http://%s/ADD' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                res =api.post(url, data=ToSend,headers=headers).json()
                self.LOGER.debug("INIT")
            else:
                self.LOGER.error("NOT ENOUGH INFO TO INIT")
        except Exception as e:
            self.LOGER.error("ERROR: %s, BAD PARAMETERS" % e)
            exit(1)

    def Select_gateway(self):
        for ag in self.GATEWAYS_LIST:
            try:
                url = 'http://%s/health' % ag
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                res =api.get(url,headers=headers).json()
                if res['status']=="OK":
                    self.API_GATEWAY = ag
                    return ag   
            except Exception:
                pass
        self.API_GATEWAY=None
        return 1


    def IndexData(self,RN,id_service,data):
        WORKSPACENAME = "SERVICEMESH"
        INDEXER=Builder(WORKSPACENAME,TPS_manager_host=self.TPSHOST) #api for index data
        try:
            INDEXER.TPSapi.format_single_query("notImportant")
        except AttributeError:
            INDEXER=Builder(WORKSPACENAME,TPS_manager_host=self.TPSHOST) #api for index data

        data_label = "%s_%s" % (RN,id_service) #this is the name of the document (mongo document)
        query = INDEXER.TPSapi.format_single_query("notImportant") #not important line. Well yes but actually no.
        res = INDEXER.TPSapi.TPS(query,"indexdata",workload=data,label=data_label) #this service (getdata) let me send json data and save it into a mongo DB
        return data_label

    def WarnGateway(self,ToSend):
        ToSend=json.dumps(ToSend)
        while(True):
            try:
                url = 'http://%s/WARN' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                res =api.post(url, data=ToSend,headers=headers).json()
                return res
            except Exception as ex:
                self.Select_gateway()
                if self.API_GATEWAY is None:
                    return {"status":"ERROR","info":"ERROR"}


    def AskGateway(self,ToSend):
        ToSend=json.dumps(ToSend)
        while(True):
            try:
                url = 'http://%s/ASK' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                res = api.post(url, data=ToSend,headers=headers).json()
                return res
            except Exception as ex:
                self.Select_gateway()
                if self.API_GATEWAY is None:
                    return {"status":"ERROR","info":"ERROR"}

        #------------------#

    def HealthCheck(self): 
        time_interval= 10
        while self._running:
            ToSend = {'status':"RUNNING","message":"Health check","label":'',"task":self.id_service,"type":'', "index":'',"control_number":self.RN}
            self.LOGER.info(ToSend)
            self.WarnGateway(ToSend)
            time.sleep(time_interval)

    def ArchiveData(self,file_pointer,namefile):
        self.LOGER.debug("ENTRO A GUARDAR DATOS")
        try:
            url = 'http://%s/ArchiveData/%s/%s' % (self.API_GATEWAY,self.RN,self.id_service)
            res = api.post(url, files={"file":(namefile,file_pointer)}).json()
            return res
        except Exception as ex:
            self.LOGER.error(ex)
            return {"status":"ERROR","info":"ERROR"}


    def run(self):
        self.status="RUNNING"
        self.HealthCheck()

    def terminate(self,final_status,last_message):
        self.status=final_status
        self._running=False
        ## send a last message
        self.WarnGateway(last_message)
        self.LOGER.warning("SENDING A LAST MESSAGE: %s" %(last_message))


    def Set_IdService(self,id_service):
        self.id_service=id_service
        
    def Set_RN(self,RN):
        self.RN=RN

        #------------------ TOOLS ---------------#
    
    def CreateMessage(self,RN,message,status,id_service=None,type_data='',parent='',label='',index_opt='',times=None):
        if id_service is None:
            id_service = self.id_service

        ToSend = {'control_number':RN, "task":id_service, 'status':status,"message":message,"parent":parent,"label":label,"type":type_data, "index":index_opt}

        if times is not None:
            ToSend['times']=times

        return ToSend