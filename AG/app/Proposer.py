import os,json,gzip
import requests as api #for APIs request
import time

class Paxos:

    def __init__ (self,arr):
        self.attempts = 5
        self.acepters = arr
        self.N = len(self.acepters)
        self.PV = 0

    def Save(self,control_number):
        """
         value = {"control_number":,"params":}
        """
        res= self.Consensus()
        if res['status']=="OK":
            value = {"control_number":control_number,"params":None}
            res= self.accept(value,action="SAVE_SOLUTION")    
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
        print("ACCEPTING")
        value = {"control_number":control_number,"params":params}
        res= self.accept(value,action="CONSULT")
        return res



##############################################################

    def prepare(self): #consensus
        attempt= 0
        while(True):
            self.PV +=1
            ToSend = json.dumps({"status":"OK","action":"PREPARE","PV":self.PV})
            
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
                print("%s nodes maked a promise" % requ_acepted)
                return {"status":"OK"}
            else:
                time.sleep(1)
                attempt+=1
                if self.attempts<attempt:
                    print("Max attempts reached... ")
                    return {"status":"ERROR"}

    def accept(self,value,action="ACCEPT"): #send request to the consensus
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
                        requ_acepted+=1
                        response = RES["value"]
                    elif RES['status']=="OK" and RES['action']=="IGNORE":
                        print("NODE IGNORED THE REQUEST")
                except Exception:
                    print("A node is down")

            
            if int(self.N/2) <requ_acepted: #mayority
                print("%s nodes ACCEPTED" % requ_acepted)
                return {"status":"OK","value":response}
            else:
                time.sleep(1)
                print("REQUEST NOT ACCEPTED... TRYING AGAIN")
                return {"status":"ERROR", "value":response}

    def Consensus(self):
        ###### PAXOS PROCESS TO REACH CONSENSUS ####
        attempt= 0
        while(True):
            print("PREPARE")
            info = self.prepare()
            if info['status']=="ERROR":
                return info
        
            print("ACCEPTING")
            value = {"control_number":"","params":""}
            res= self.accept(value)
            if res['status'] == "OK":
                return {"status":"OK"}
            else:
                attempt+=1
                if self.attempts<attempt:
                    print("Max attempts reached... ")
                    return {"status":"ERROR"}
        #############################################








