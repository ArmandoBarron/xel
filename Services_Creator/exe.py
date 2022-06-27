import json, os, time, subprocess
from datetime import datetime

with open('conf.json', 'r') as f:
        conf = json.load(f)['exe']
f.close()

def create_service(parent,data,string,tab):
    tab = tab + "  "
    if(type(data) is dict):
        string = string + tab + parent + ": \n"
        for key in data:
            string = create_service(key,data[key],string,tab)
    elif(isinstance(data,list)):
        total_childs = len(data)
        string = string + tab + parent + ": \n"
        for i in range(total_childs):
            string = string + tab + "  - " + data[i] + "\n"
    else:
        string = string + tab +parent+": "+data+"\n"
        tab = "  "
        
    return string
    
            
            
def create_dockerfile(data2,names,services,resultfile_id):
    
    total_services = len(services)
    string = "version: '3'\nservices:\n"
    for i in range(total_services):
        tab = ""
        service_name = services[i]
        data = data2[services[i]]
        container_name = names[service_name]
        
        data['environment']['SERVICE_NAME'] = service_name
        data['environment']['SERVICE_IP'] = container_name
        data['environment']['NETWORK'] = str(resultfile_id)
        #string = string + tab + container_name+":"+"\n"
        string_service = create_service(container_name,data,"",tab)
        string = string + string_service + "\n"
        del string_service
        
        
        #for key in data:
        #    if(type(data[key]) is dict):
        #        string = string+parent_tab+key+": \n"
        #        for key2 in data[key]:
        #            string = string + child_tab+key2+": "+data[key][key2]+"\n"
        #    elif(isinstance(data[key],list)):
        #        string = string+parent_tab+key+": \n"
        #        total_childs = len(data[key])
        #        for i in range(total_childs):
        #            string = string + child_tab+" - "+data[key][i]+"\n"
        #        
        #    else:
        #        string = string + parent_tab+key+": "+data[key]+"\n"
        #string = string + "\n\n"
        
    
    #footer
    string += "networks:\n \
    service_mesh:\n\
        name: xel_service_mesh"

    print(string)
    return string

def get_childs(childs_list, data):
    total_parents = len(data)
    for i in range(total_parents):
        childs_list.append(data[i]['service'])
        if(len(data[i]["childrens"]) > 0):
            get_childs(childs_list,data[i]['childrens'])

def get_id():
    # datetime object containing current date and time
    return(datetime.now().strftime("%d%m%Y%H%M%S"))


def execute(request):    
    
    
    
    resultfile_location = conf['resultfile_location']
    resultfile_extension = conf['resultfile_extension']
    resultfile_id = get_id()
    
    resources_location = conf['resources_location']
    resources_name = conf['resources_name']
    resources_extension = conf['resources_extension']
    
    resources_filename = resources_location + resources_name + resources_extension
    
    with open(resources_filename, 'r') as f:
        data = json.load(f)
    f.close()

    resources = data[conf['resources_key']]
    names = data[conf['names_key']]

    childs_list = []
    get_childs(childs_list,request)

    #To replicate
    childs_list = list(set(childs_list))


    docker_content = create_dockerfile(resources, names, childs_list, resultfile_id)
    
    resultfile_filename = resultfile_location + resultfile_id + resultfile_extension
    f = open(resultfile_filename, "w")
    f.write(docker_content)
    f.close()
    
    services_created_string = output = error = None
    try:
        command = 'docker-compose -f '+resultfile_filename+' ps --services'
        services_created_string = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print (e.output)
        return False,e.output
    
    services_created_array = sorted(services_created_string.split("\n"))
    print(services_created_array)
    
    try:
        command = 'docker-compose -f '+resultfile_filename+' up -d'
        os.system(command)
    except subprocess.CalledProcessError as e:
        print(e.output)
        return False,e.output
    
    try:
        command = 'docker-compose -f '+resultfile_filename+' ps --services --filter "status=running"'
        services_running_string = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(e.output)
        return False,e.output
            
    services_running_array = sorted(services_running_string.split("\n"))
    print(services_running_array)
    

    if(services_created_array == services_running_array):        
        return True,resultfile_id
    return False, conf['create_services_finalerror']