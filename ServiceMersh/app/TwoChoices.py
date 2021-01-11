from random import randint
from random import seed

class loadbalancer():

    def __init__(self,resources):
        # dictionary['services']    [service][resources]=[]
        self.resources= resources


    def decide(self,service):
        list_of_res= self.resources[service]['resources']
        total_resources = len(list_of_res)
            
        random1 = randint(0, total_resources-1)
        random2 = randint(0, total_resources-1)
            
        if(self.resources[service]['resources'][random1]['workload'] <= self.resources[service]['resources'][random2]['workload']):
            self.resources[service]['resources'][random1]["workload"]+=1
            return self.resources[service]['resources'][random1]

        else:
            self.resources[service]['resources'][random2]["workload"]+=1
            return self.resources[service]['resources'][random2]


