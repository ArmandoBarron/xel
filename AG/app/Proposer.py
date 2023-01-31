import os,json,gzip
import requests as api #for APIs request
import time

class Paxos:

    def __init__ (self,arr):
        self.attempts = 20
        self.acepters = arr
        self.N = len(self.acepters)
        self.PV = 0

    def Save(self,control_number,DAG,auth):
        """
         value = {"control_number":,"params":}
        """
        res= self.Consensus()
        if res['status']=="OK":
            value = {"control_number":control_number,"params":None,'DAG':DAG,"auth":auth}
            res= self.accept(value,action="SAVE_SOLUTION")    
        return res
    
    def Store(self,control_number,DAG,meta,auth):
        """
         value = {"control_number":,"metadata":,"DAG",auth"}
        """
        res= self.Consensus()
        if res['status']=="OK":
            value = {"control_number":control_number,"metadata":meta,"auth":auth,'DAG':DAG}
            res= self.request2node(value,action="STORE_SOLUTION")    
        return res
    
    def Retrieve(self,token_solution,auth):
        """
         value = {"control_number":,auth"}
        """

        value = {"control_number":token_solution,"auth":auth}
        res= self.request2node(value,action="RETRIEVE_SOLUTION")

        return res

    def Delete(self,token_solution,auth):
        """
         value = {"control_number":,auth"}
        """

        value = {"control_number":token_solution,"auth":auth}
        res= self.request2node(value,action="DELETE_SOLUTION")

        return res
    
    def list_solutions(self,auth,params=None):
        """
         value = {"control_number":,auth"}
        """
        res= self.Consensus()
        if res['status']=="OK":
            value = {"auth":auth,"params":params}
            res= self.request2node(value,action="LIST_SOLUTIONS")    
        return res
    

    def Update_task(self,control_number,params):
        """
         value = {"control_number":,"params":}
        """
        value = {"control_number":control_number,"params":params}
        res= self.accept(value,action="UPDATE_TASK")
        return res


    def Consult(self,control_number,params=None):
        """
         value = {"control_number":,"params":}
        """
        value = {"control_number":control_number,"params":params}
        res= self.accept(value,action="CONSULT")
        return res

    def Consult_v2(self,token_project,control_number,tasks,params=None,kind_task="task_list",show_history=None):
        """
         value = {"control_number":,"params":}
        """
        value = {"control_number":control_number,"token_project":token_project,"params":params,"kind_task":kind_task}
        if tasks is not None:
            value['monitoring_tasks']=tasks
        if show_history is not None:
            value['show_history']=show_history

        res= self.accept(value,action="CONSULT_V2")
        return res
## ========================================================= ##
## ====================== RESOURCES ======================== ##
## ========================================================= ##

    def Read_resource(self,service,service_id,context,read_action="SELECT"):
        #res= self.Consensus()
        #if res['status']=="OK":
        value = {
            "action":read_action,
            "action_params":{'service':service,'service_id':service_id,"context":context},
            "data_bin":{}
        }
        res= self.request2node(value,action="RESOURCES")    
        return res

    def Update_resource(self,service,service_id,data_bin,read_action="ADD"):
        res= self.Consensus()
        if res['status']=="OK":
            value = {
                "action":read_action,
                "action_params":{'service':service,'service_id':service_id},
                "data_bin":data_bin
            }
            res= self.accept(value,action="RESOURCES")    
        return res

##############################################################

    def prepare(self): #consensus
        attempt= 0
        self.PV +=1
        v = self.PV

        while(True):


            ToSend = json.dumps({"status":"OK","action":"PREPARE","PV":v})
            
            #send it to all acepters
            requ_acepted=0
            for ac in self.acepters:
                url = 'http://%s/REQUEST' % ac['host']

                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                try:
                    result = api.post(url, data=ToSend,headers=headers)
                    RES = result.json()
                    if RES['status']=="OK" and RES['action']=="PROMISE":
                        requ_acepted+=1
                except Exception:
                    print("A node is down")

            
            if int(self.N/2) <requ_acepted: #mayority
                #print("%s nodes maked a promise" % requ_acepted)
                return {"status":"OK","PV":v}
            else:
                time.sleep(.1)
                attempt+=1
                if self.attempts<attempt:
                    #print("Max attempts reached... ")
                    return {"status":"ERROR"}


    def accept(self,value,pv=0,action="ACCEPT"): #send request to the consensus
            response = None
            ToSend = json.dumps({"status":"OK","action":action,"PV":pv,"value":value})
            
            #send it to all acepters
            requ_acepted=0
            for ac in self.acepters:
                url = 'http://%s/REQUEST' % ac['host']
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                try:
                    result = api.post(url, data=ToSend,headers=headers)
                    RES = result.json()
                    if RES['status']=="OK" and RES['action']=="ACCEPT":
                        requ_acepted+=1
                        response = RES["value"]
                    elif RES['status']=="OK" and RES['action']=="IGNORE":
                        pass
                    elif RES['status']=="ERROR":
                        response = RES["value"]
                        return {"status":"ERROR", "value":response}
                except Exception:
                    print("A node is down")

            
            if int(self.N/2) <requ_acepted: #mayority
                return {"status":"OK","value":response}
            else:
                time.sleep(.2)
                return {"status":"ERROR", "value":response}

    def request2node(self,value,action="ACCEPT"): 
        #send a request directly to 1 node
            response = None
            ToSend = json.dumps({"status":"OK","action":action,"PV":self.PV,"value":value})
            
            #send it to all acepters
            requ_acepted=0
            for ac in self.acepters:
                url = 'http://%s/REQUEST' % ac['host']
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                try:
                    result = api.post(url, data=ToSend,headers=headers)
                    RES = result.json()
                    if RES['status']=="OK" and RES['action']=="ACCEPT":
                        response = RES["value"]
                        break;
                    elif RES['status']=="OK" and RES['action']=="IGNORE":
                        pass
                    elif RES['status']=="ERROR":
                        response = RES["value"]
                        return {"status":"ERROR", "value":response}
                except Exception:
                    print("A node is down")

            if response is not None:
                return {"status":"OK","value":response}
            else:
                return {"status":"ERROR", "value":response}

    def Consensus(self):
        ###### PAXOS PROCESS TO REACH CONSENSUS ####
        attempt= 0
        while(True):
            info = self.prepare()
            if info['status']=="ERROR":
                return info
        
            #print("ACCEPTING")
            value = {"control_number":"","params":""}
            res= self.accept(value,pv=info['PV'])
            if res['status'] == "OK":
                return {"status":"OK"}
            else:
                attempt+=1
                if self.attempts<attempt:
                    #print("Max attempts reached... ")
                    return {"status":"ERROR"}
        #############################################








