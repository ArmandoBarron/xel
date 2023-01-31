#import building_middleware as BB ##importing middleware
import logging #logger
import socket,os,sys,pickle,json,pandas
import time
import C
import tempfile
import tqdm
import base64

class bb_dispatcher():

    def __init__(self,TOKEN_SOLUTION,SERVICE_ID,CONTEXT,LOGER=None,POSTMAN=None,Tolerant_errors=2):
        
        if LOGER is None:
            self.LOGER = logging.getLogger()
        else:
            self.LOGER=LOGER

        ####
        self.TOKEN_SOLUTION=TOKEN_SOLUTION
        self.PARENT=SERVICE_ID
        self.CONTEXT=CONTEXT
        self.POSTMAN=POSTMAN
        self.Tolerant_errors=Tolerant_errors


    def Send_to_BB(self,data_map,data_pointer,auth,child,parent = None):
        if parent is None:
            parent = self.PARENT

        self.LOGER.info("### INFO: file: %s ..." %data_map['type'])

        child['control_number']=self.TOKEN_SOLUTION ## add control number 
        
        ######## ASK #######
        ToSend = {'service':child['service'],'context':self.CONTEXT}
        res = self.POSTMAN.AskGateway(ToSend)
        #------------------#
        if 'info' in res: #no more nodes
            self.LOGER.error("NO NODES FOUND")
            data = self.POSTMAN.CreateMessage(self.TOKEN_SOLUTION,'no available resources found.','ERROR',id_service=child['id'])
            self.POSTMAN.WarnGateway(data)
        else:
            errors_counter=0
            ###### SEND #######
            ip = res['ip'];port = res['port']
            self.LOGER.debug("Children >>>>>> IP:%s PORT: %s " %(ip,port) )
            while(True):
                #
                data = C.RestRequest(ip,port,{'data':data_map,'DAG':child,"auth":auth},data_file=data_pointer)
                if data is not None:
                    self.LOGER.info(">>> DATA SENT SUCCESFULLY <<<")
                    #warn successful process
                    ToSend = self.POSTMAN.CreateMessage(self.TOKEN_SOLUTION,'Starting ejecution.','INFO',id_service=child['id'],parent=parent,dag=child)
                    
                    self.POSTMAN.WarnGateway(ToSend)
                    errors_counter=0
                    break;
                else:
                    errors_counter+=1
                    self.LOGER.warning(">>>>>>> NODE FAILED... TRYING AGAIN..%s" % errors_counter)
                    if errors_counter>=self.Tolerant_errors: #we reach the limit
                        ######## ASK AGAIN #######
                        ToSend = {'service':child['service'],'context':self.CONTEXT,'update':{'id':res['id'],'status':'DOWN'}} #update status of falied node
                        res = self.POSTMAN.AskGateway(ToSend)
                        #------------------#
                        errors_counter=0 #reset counter 
                        if 'info' in res: #no more nodes
                            data = self.POSTMAN.CreateMessage(self.TOKEN_SOLUTION,'no available resources found: %s attempts.' % str(errors_counter) ,'ERROR',id_service=child['id'])
                            self.POSTMAN.WarnGateway(data)
                            break
                        ip = res['ip'];port = res['port']
                        self.LOGER.debug("TRYING A NEW NODE... IP:%s PORT: %s " %(ip,port) )


