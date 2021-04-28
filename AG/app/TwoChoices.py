from random import randint
from random import seed
import json
class loadbalancer():

    def __init__(self,dictionary):

        # dictionary['services']    [service][resources]=[]
        self.dictionary = dictionary
        self.resources= dictionary['services']
        self.force_local = dictionary["config"]['force_lan_selection']
        self.gateways = dictionary['internal_gateways']


    def decide(self,service,network,force_network=None,n=1):
        if force_network is None:
            force_network = self.force_local
        
        up_resources=[]
        for r in self.resources[service]['resources']: #up services
            if r['status'] == "UP":
                up_resources.append(r)


        network_resources = []
        for r in up_resources: #services in the same network
            if r['network'] == network and force_network:
                network_resources.append(r)

        total_resources = len(network_resources)

        if total_resources <=0:
            if len(up_resources)<=0: #actually there are no resources
                return None
            resources = up_resources #select all up resources despite the network
            total_resources = len(resources)
        else:
            resources = network_resources

        # two choices algorithm
        random1 = randint(0, total_resources-1)
        random2 = randint(0, total_resources-1)
        if total_resources>1: #more than 1 resource
            while(True):
                if random1 == random2:
                    random1 = randint(0, total_resources-1)
                else:
                    break




        
        if(resources[random1]['workload'] <= resources[random2]['workload']):
            self.AddWorkload(service,random1,n=n)
            return resources[random1]
        else:
            self.AddWorkload(service,random1,n=n)
            return resources[random2]

    def AddWorkload(self,service,id_service,n=1):
        for r in self.resources[service]['resources']:
            if r["id"]==id_service:
                r["workload"]+=n

    def NodeDown(self,service,id_service):
        for r in self.resources[service]["resources"]:
            if r['id']==id_service:
                r['status']="DOWN"

    def NodeUP(self,service,id):
        for r in self.resources[service]["resources"]:
            if r['id']==id_service:
                r['status']="UP"

    def GetStatus(self):
        return self.resources

    def NetworkDown(self,service,network):
        for r in self.resources[service]["resources"]:
            if r['network']==network:
                r['status']="DOWN"

    def SelectGateway(self,opt1):
        resources = self.gateways
        for res in resources:
            if res['network']==opt1 and res['status']=="UP":
                return res
        return None #there is no api gateway

    def GatewayDown(self,id_gateway):
        for r in self.gateways:
            if r['id']==id_gateway:
                r['status']="DOWN"

    def Addresource(self,service,data):
        if service == "gateway" or service == "GATEWAY":
            for res in self.gateways:
                if res['ip']==data['ip'] and res['port']==data['port'] and res['network']==data['network']:
                    res['status']="UP"
                    return False
            #if not
            id_service = len(self.gateways)+1
            self.gateways.append({"network":data['network'],"id":id_service,"ip":data['ip'],"port":data['port'],"status":"UP"})
            return True
        else:
            #verify if exist        
            for res in self.resources[service]["resources"]:
                if res['ip']==data['ip'] and res['port']==data['port'] and res['network']==data['network']:
                    res['status']="UP"
                    return False

            #if not, add as a new resource
            id_service = len(self.resources[service]["resources"])+1
            self.resources[service]["resources"].append({"network":data['network'],"id":id_service,"ip":data['ip'],"port":data['port'],"workload":0,"status":"UP"})
            return True


    def Save_config_file(self):
        self.dictionary['services'] = self.resources
        self.dictionary['internal_gateways'] = self.gateways

        with open('coordinator_structure.json', 'w') as f:
            json.dump(self.dictionary, f ,indent=2)