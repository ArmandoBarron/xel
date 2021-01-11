import os,json,gzip
import requests as api #for APIs request
import time

class Paxos:

    def __init__ (self,arr):
        self.acepters = arr
        self.N = len(self.acepters)
        self.PV = 0

    def process(self):
        while(True):
            print("PREPARE")
            self.prepare()
            print("ACCEPTING")
            res= self.accept()
            if res != "ERROR":
                print("DONE")
                break

    def prepare(self):
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

            
            if int(self.N/2) <=requ_acepted: #mayority
                print("%s nodes maked a promise" % requ_acepted)
                return "OK"
            else:
                time.sleep(1)

    def accept(self):
            ToSend = json.dumps({"status":"OK","action":"ACCEPT-REQUEST","PV":self.PV,"value":"service"})
            
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
                    elif RES['status']=="OK" and RES['action']=="IGNORE":
                        print("NODE IGNORED THE REQUEST")
                except Exception:
                    print("A node is down")

            
            if int(self.N/2) <=requ_acepted: #mayority
                print("%s nodes ACCEPTED" % requ_acepted)
                return "OK"
            else:
                time.sleep(1)
                print("RESUEST NOT ACCEPTED... TRYING AGAIN")
                return "ERROR"

#ACCEPT

#return request







