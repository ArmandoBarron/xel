from threading import Thread
import time
import requests as api #for APIs request
import logging
import json
#from TPS.Builder import Builder #TPS API BUILDER
import tempfile
import shutil
import cgi
import multiprocessing as mp
from threading import Thread
import os
import hashlib

class postman(Thread):

    def __init__(self,GATEWAYS_LIST,SERVICE,SERVICE_IP,SERVICE_PORT,NETWORK,TPSHOST,API_GATEWAY=None,LOGER=None,tokenuser=None):
        #super(postman, self).__init__()
        Thread.__init__(self)
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
        self.CONTEXT=NETWORK
        self.TPSHOST=TPSHOST
        self.API_KEY=os.getenv("API_KEY")
        self.TOKENUSER=tokenuser
        ##################
        self.status = "STANDBY"
        self.RN=None
        self.id_service = None
        self.last_message ={}
        self._running=True
        self.hash_product=""
        self.times ={
            "id":"",
            "acq":0,
            "serv":0,
            "trans":0,
            "exec":0,
            "idx":0,
            "comm":0
        } 



    def init_service(self):
        try:
            if self.SERVICE is not None and self.SERVICE_IP is not None and self.SERVICE_PORT is not None:
                ToSend=json.dumps({"SERVICE":self.SERVICE,"ID":self.SERVICE_IP,"IP":self.SERVICE_IP,"PORT":int(self.SERVICE_PORT),"CONTEXT":self.CONTEXT})
                url = 'http://%s/ADD' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}

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
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
                res =api.get(url,headers=headers).json()
                if res['status']=="OK":
                    self.API_GATEWAY = ag
                    return ag   
            except Exception:
                pass
        self.API_GATEWAY=None
        return 1


    def MonitorService(self,token_project,token_solution):
        try:
            t = time.time()
            url = "http://%s/monitor/v2/%s/%s" % (self.API_GATEWAY,token_project,token_solution)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
            res =api.get(url,headers=headers).json()
            self.times['comm']+= time.time()-t
            if res['status']=="OK":
                return res
            return None
        except Exception:
            return None

    def MonitorSpecificService(self,token_project,token_solution,list_task,kind="task_list"):
        try:
            t = time.time()
            ToSend=json.dumps({"tasks":list_task,"kind_task":kind})
            url = "http://%s/monitor/v2/%s/%s" % (self.API_GATEWAY,token_project,token_solution)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
            res =api.post(url,data=ToSend,headers=headers).json()
            self.times['comm']+= time.time()-t
            if res['status']=="OK":
                return res
            return None
        except Exception:
            return None
        
    def ValidateSubtask(self,token_solution,task_list):
        try:
            t = time.time()
            ToSend=json.dumps({"token_solution":token_solution,"task_list":task_list})
            url = "http://%s/Validate_subtask_executions" % (self.API_GATEWAY)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
            res =api.post(url,data=ToSend,headers=headers).json()
            self.times['comm']+= time.time()-t
            if res['status']=="OK":
                return res
            return None
        except Exception:
            return None


    def VisualProducts_Map_Manager(self,action, token_solution, token_dispatcher='',token_producer='',data_obj='',levels=[] ):
        """
        function to send a request to the visual product object to, update, create, get, delete and clean

        value {
            action::create, delete, clean, update,get
            token_solution: "",
            token_dispatcher:"",
            token_producer:"",
            data_obj: {}
        }

            data obj could be
                {"path":"L1=val1","levels":{},"products":list_porducts};
                                            or
                {"id":dag["id"],"alias":"","service":dag["service"],"params":dag["params"]}


            products:{
                level:{
                    id:{alias,name,id}
                    }
                }
            }
        """
        ToSend=json.dumps({"action":action,"token_solution":token_solution,
                           "token_dispatcher":token_dispatcher,
                           "token_producer":token_producer,
                           "data_obj":data_obj,
                           "levels":levels})
        t=time.time()
        while(True):
            try:
                url = 'http://%s/ProductsObjectMap' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
                res =api.post(url, data=ToSend,headers=headers).json()
                self.times['comm']+= time.time()-t
                return res
            except Exception as ex:
                self.Select_gateway()
                if self.API_GATEWAY is None:
                    return {"status":"ERROR","info":"ERROR"}

    def GetResults(self,token_solution,task,auth):
        """Download file from url to directory

        URL is expected to have a Content-Disposition header telling us what
        filename to use.

        Returns filename of downloaded file.

        """
        t = time.time()


        while(True):
            # primero se verifica que la tarea haya terminado
            kind = "subtask_list"
            res_monitor = self.MonitorSpecificService(auth['user'],token_solution,[task],kind=kind)

            file_is_ready = False
            if task in res_monitor['list_task']: 
                task_info = res_monitor["list_task"][task]
                if task_info['status']=="OK" or task_info['status']=="FINISHED":                
                    file_is_ready = True
                elif task_info['status']=="ERROR" or task_info['status']=="FAILED":
                    ext="error"
                    file_group = tempfile.NamedTemporaryFile(delete=False,suffix="."+ext) # TEMPORARY FILE TO SAVE DATA
                    fname = file_group.name
                    file_group.close()
                    break
                else:
                    self.LOGER.error("No hay estatus correcto, los datos no estan listos aun")
            else:
                self.LOGER.error("La tarea no esta en la lista %s" % kind)



            if file_is_ready:
                ToSend = {'data':{},'type':""}
                ToSend["data"]["token_user"]=auth['user']
                ToSend["data"]["token_solution"]=token_solution 
                ToSend["data"]["task"]=task
                ToSend["data"]["catalog"]=auth['workspace']
                ToSend["type"] ="SOLUTION"

                ToSend=json.dumps(ToSend)
                url = 'http://%s/getfile' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
                response = api.post(url, data=ToSend,headers=headers,stream=True)

                try:
                    params = cgi.parse_header(
                            response.headers.get('Content-Disposition', ''))[-1]
                    ext = params['filename'].split(".")[-1]


                    file_group = tempfile.NamedTemporaryFile(delete=False,suffix="."+ext) # TEMPORARY FILE TO SAVE DATA
                    fname = file_group.name
                    file_group.close()
                    with open(fname, 'wb') as target:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, target)
                    break
                except KeyError as ke:
                    self.LOGER.error("Se generó un error porque los datos de entrada aun no estan listos")
            
            time.sleep(5) #el archivo aun no esta listo


            
        self.times['acq']+= time.time()-t
        return {"data":fname,"type":ext}

    def ReportTimes(self):
        ToSend=json.dumps({"token_solution":self.RN,"times":self.times})
        while(True):
            try:
                t=time.time()
                url = 'http://%s/report_time' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
                res =api.post(url, data=ToSend,headers=headers).json()
                return res
            except Exception as ex:
                self.Select_gateway()
                if self.API_GATEWAY is None:
                    return {"status":"ERROR","info":"ERROR"}


    def WarnGateway(self,ToSend):
        task = ToSend['task']
        ToSend=json.dumps(ToSend)
        t=time.time()
        while(True):
            try:
                url = 'http://%s/WARN' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
                res =api.post(url, data=ToSend,headers=headers).json()
                if res['status']=="ERROR": #paxos denied the request
                    self.LOGER.error("record of %s FAILED. trying again..." %  task)
                else:
                    self.times['comm']+= time.time()-t
                    return res
            except Exception as ex:
                self.Select_gateway()
                if self.API_GATEWAY is None:
                    return {"status":"ERROR","info":"ERROR"}


    def AskGateway(self,ToSend):
        ToSend=json.dumps(ToSend)
        while(True):
            try:
                t= time.time()
                url = 'http://%s/ASK' % self.API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
                res = api.post(url, data=ToSend,headers=headers).json()
                self.times['comm']+= time.time()-t
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
            self.WarnGateway(ToSend)
            self.LOGER.info("================ HEALTHCHECK COMPLETE =================== %s " % self._running)
            time.sleep(time_interval)
        return True

    def ArchiveData(self,data_path,namefile, id_service=None,mining_statistics=False,metadata={}):
        if id_service is None:
            id_service=self.id_service
        
        t = time.time()
        
        self.LOGER.info("Guardando %s" %id_service)
        self.calculate_sha256sum(data_path)
        self.LOGER.info("Hash resultant product: %s" % self.hash_product)
        try:
            file_pointer = open(data_path,"rb")
            headers = {'x-access-token': self.API_KEY}
            cookies={}
            if mining_statistics:
                cookies = {'x-mining-statistics':"True"}
            cookies["metadata"] = json.dumps(metadata)
            self.LOGER.info(cookies)

            url = 'http://%s/ArchiveData/%s/%s' % (self.API_GATEWAY,self.RN,id_service)
            res = api.post(url, files={"file":(namefile,file_pointer)},headers=headers,cookies=cookies).json()
            self.times['idx']+= time.time()-t
            file_pointer.close()
            del file_pointer
            return res
        except Exception as ex:
            self.LOGER.error(ex)
            file_pointer.close()
            return {"status":"ERROR","info":"ERROR"}


    def run(self):
        self.status="RUNNING"
        #introducing itself
        self.HealthCheck()
        return True

    def terminate(self,final_status,last_message):
        self.status=final_status
        self._running=False


        ## send a last message
        self.WarnGateway(last_message)
        self.LOGER.warning("SENDING A LAST MESSAGE: %s" %(last_message))

    def calculate_sha256sum(self,filename):
        h  = hashlib.sha256()
        b  = bytearray(128*1024)
        mv = memoryview(b)
        with open(filename, 'rb', buffering=0) as f:
            while n := f.readinto(mv):
                h.update(mv[:n])
        self.hash_product = h.hexdigest()

    def Set_IdService(self,id_service):
        self.id_service=id_service
        self.times['id']=id_service
        
    def Set_RN(self,RN):
        self.RN=RN

    def Get_Times(self,key=None):
        if key is None:
            return self.times
        else:
            return self.times[key]
    
    def GetReference(self,query,ENV={}):
        try:
            ToSend=json.dumps({"query":query,"ENV":ENV})
            url = "http://%s/reference/get" % (self.API_GATEWAY)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'x-access-token': self.API_KEY}
            res =api.post(url,data=ToSend,headers=headers).json()
            self.LOGER.error(res)
            if res['status']=="OK":
                return res["value"]
            return None
        except Exception as e:
            self.LOGER.error("EXPETION: %s" % e)
            return None

    def Set_Time(self,time_key,value,operation="replace"):
        if operation=="replace":
            self.times[time_key]=value

        #------------------ TOOLS ---------------#
    def ValidateDataMap(self,data_map,auth):
        if data_map['type']=="SOLUTION": #se adquieren los datos
            data_map['data'] = data_map['data'].replace(".SOLUTION","") #se le añadio esta extencion, por lo que hay que quitarla
            data_map = self.GetResults(self.RN,data_map['data'],auth)
            self.calculate_sha256sum(data_map['data'])
            #index hash
            ToSend = self.CreateMessage(self.RN,"indexing input data hash","UPDATE",type_data=data_map['type'],include_hash=True)
            self.WarnGateway(ToSend)
            
        return data_map
    
    def CreateMessage(self,RN,message,status,id_service=None,type_data='',parent='',label='',index_opt='',times=None,dag=None,include_hash=False):
        if id_service is None:
            id_service = self.id_service

        ToSend = {'control_number':RN, "task":id_service, 'status':status,"message":message,"parent":parent,"label":label,"type":type_data, "index":index_opt}

        if times is not None:
            ToSend['times']=times

        if dag is not None:
            ToSend['dag']=dag

        if include_hash:
            ToSend['hash_product'] = self.hash_product


        return ToSend
