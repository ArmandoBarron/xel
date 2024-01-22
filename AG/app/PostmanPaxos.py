import time
import logging
import json
import hashlib

class postman():

    def __init__(self,PROPOSER,LOGS_FOLDER,service=None,LOGER=None,hash_product=""):
        #super(postman, self).__init__()
        if LOGER is None:
            self.LOGER = logging.getLogger()
        else:
            self.LOGER=LOGER

        ####
        self.id_service = service
        self.PROPOSER=PROPOSER
        self.logs_folder = LOGS_FOLDER
        self.hash_product=hash_product

    def WarnGateway(self,warn_message):
        #ToSend={'status':status,"message":message,"label":label,"task":id_serv,"type":data_type, "index":index_opt} #update status
        control_number = warn_message['control_number']
        ######## paxos ##########
        paxos_response = self.PROPOSER.Update_task(control_number,warn_message) # save request in paxos distributed memory
        if paxos_response['status'] == "ERROR":
            self.LOGER.error("PAXOS PROTOCOL DENIED THE REQUEST")
            return json.dumps({'status':'ERROR',"message":"PAXOS DENIED THE REQUEST"})
        #########################

        if 'times' in warn_message:
            tmp= warn_message['times']
            f = open(self.logs_folder+'log_'+control_number+'.txt', 'a+'); 
            f.write("%s, %s, %s, %s \n" %(tmp['NAME'],tmp['ACQ'],tmp['EXE'],tmp['IDX'], )) 
            f.close()
            del f
        return {'status':'OK'}
    
    def AskGateway(self,params):
        service = params['service'] #service name
        context = params['context']
        n=1 #quantity of workload added to resource
        force = True
        if 'force' in params: #option for gateways, gateways are forced to select a resource in the same context
            force = True
            n = 0

        if 'update' in params: #update node status
            info = params['update'] #{id,status,type}
            if info['status'] == "DOWN":
                self.PROPOSER.Update_resource(service,info['id'],{"context":context},read_action="DISABLE")

        res = self.PROPOSER.Read_resource(service,'',context,read_action="SELECT")['value'] #select

        if res is None: #no more avaiable resources
            return {'info':'ERROR'}
        else:
            self.PROPOSER.Update_resource(service,res['id'],{"context":res['context']},read_action="ADD_WORKLOAD")
            return res
        
    def calculate_sha256sum(self,filename):
        h  = hashlib.sha256()
        b  = bytearray(128*1024)
        mv = memoryview(b)
        with open(filename, 'rb', buffering=0) as f:
            while n := f.readinto(mv):
                h.update(mv[:n])
        hash_product = h.hexdigest()
        self.hash_product = hash_product
        return hash_product
    
    def set_hash(self,hash):
        self.hash_product = hash
    
    def CreateMessage(self,RN,message,status,id_service=None,type_data='',parent='',label='',index_opt='',times=None,dag=None,include_hash=False,token_user=None):
        if id_service is None:
            id_service = self.id_service

        ToSend = {'control_number':RN, "task":id_service, 'status':status,"message":message,"parent":parent,"label":label,"type":type_data, "index":index_opt}

        if times is not None:
            ToSend['times']=times

        if dag is not None:
            ToSend['dag']=dag

        if include_hash:
            ToSend['hash_product'] = self.hash_product

        if token_user is not None:
            ToSend['token_user'] = token_user

        return ToSend
