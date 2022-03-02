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


    def decide(self,service,context,force_context=None,n=1):
        if force_context is None:
            force_context = self.force_local
        try:
            # look for up services
            resources_tobe_used = self.LookingForInResources(service,'status',True)

            # look for services in same context
            if force_context:
                resources_tobe_used = self.LookingForInResources(service,'context',context,dict_resources=resources_tobe_used)

            #convert them to a list
            resources =[]
            for key,value in resources_tobe_used.items():
                resources.append(value)

            total_resources = len(resources)
            if total_resources <=0:
                return None

            # two choices algorithm
            random1 = randint(0, total_resources-1)
            random2 = randint(0, total_resources-1)
            if total_resources>1: #more than 1 resource
                while(True):
                    if random1 == random2:
                        random1 = randint(0, total_resources-1)
                    else:
                        break
        except KeyError: #the service required is not in the mesh
            return None


        if(resources[random1]['workload'] <= resources[random2]['workload']):
            service_id = resources[random1]['id']
            return resources[random1]
        else:
            service_id = resources[random2]['id']
            return resources[random2]

    def AddWorkload(self,service,id_service,n=1):
        self.resources[service][id_service]["workload"]+=n

    def NodeDown(self,service,id_service):
        self.resources[service][id_service]['status']=False

    def NodeUP(self,service,id):
        self.resources[service][id_service]['status']=True

    def GetStatus(self):
        return self.resources

    def Addresource(self,service,service_id,data):
        #verify if the service exist
        if service not in self.resources:
            self.resources[service] = {}
            
        #verify if resource exist
        if service_id in self.resources[service]:
            return False
        else:
            self.resources[service][service_id]=data
            return True


    def Save_config_file(self):
        self.dictionary['services'] = self.resources
        self.dictionary['internal_gateways'] = self.gateways

        with open('coordinator_structure.json', 'w') as f:
            json.dump(self.dictionary, f ,indent=2)

    def LookingForInResources(self,service,looking_for,with_value,dict_resources=None):
        result_dict={}
        if dict_resources is None:
            dict_resources=self.resources[service]
        
        for resource_id,value in dict_resources.items():
            if value[looking_for] == with_value:
                result_dict[resource_id] = value #se añaden al dict todos los que cumplan la condicion

        return result_dict