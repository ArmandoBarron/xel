import json, os, time, subprocess
from datetime import datetime

API_KEY=os.getenv("API_KEY") #a sha256 hash (eg. "9aa491c85508cfeead30c569c88c8f26e3881792a3f158a323ee9ac6150ab1cd") 


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


def create_nez_cfgfile(data2,names,services,resultfile_id, replicate_dictionary):

    total_services = len(services)
    string = "#./deployer/app/cfg-files/xelhua.cfg\n"
    stages_list = []
    URL_REPO = os.getenv("IMAGES_REPO_URL")
    KIND_REPO = os.getenv("IMAGES_REPO")

    for i in range(total_services):
        string+="[BB]\n" 
        service_name = services[i]
        service_params = data2[service_name]

        service_params['environment']['SERVICE_NAME'] = service_name
        service_params['environment']['SERVICE_IP'] = service_name
        service_params['environment']['NETWORK'] = str(resultfile_id)

        string+="name = %s \n" % service_name
        string+="command = ls\n"
        if KIND_REPO == "remote":
            string+="image = %s%s\n" % (URL_REPO,service_params["image"])
        else:
            string+="image = %s\n" % service_params["image"]

        
        enviroment_values = ""
        for k,v in service_params["environment"].items():
            enviroment_values+="%s=%s;" %(k,v)
        enviroment_values+="API_KEY=%s;" %(API_KEY)
        string+="environment  = %s \n[END]\n\n" % enviroment_values

        #create pattern
        replicates_service = replicate_dictionary[service_name]
        string+='[PATTERN]\n'
        string+= "name = %spattern\n" % service_name
        string+= "task = %s\n" % service_name
        string+= "pattern = MW\n"
        string+= "workers = %s\n" % replicates_service
        string+= "loadbalancer = TC:DL\n"
        string+='[END]\n\n'

        #create stage
        string+='[STAGE]\n'
        string+= "name = stage_%s\n" % service_name
        string+= "source = @PWD/xelhua/inputs\n"
        string+= "sink = \n"
        string+= "transformation = %spattern\n" % service_name
        string+='[END]\n\n'

        stages_list.append("stage_%s" % service_name)

    string+='[WORKFLOW]\n'
    string+= "name = %s\n" % resultfile_id
    string+= "stages = %s\n" % " ".join(stages_list)
    string+= "network = xel_service_mesh\n"
    string+= "memory = 1024M\n"
    string+= "memory_limit = 3072M\n"
    string+= "CPUS = 2\n"

    string+='[END]\n\n'

    print(string)
    return string

            
def create_dockerfile(data2,names,services,resultfile_id, replicate_dictionary):
    
    total_services = len(services)
    string = "version: '3'\nservices:\n"
    for i in range(total_services):
        tab = ""
        service_name = services[i]
        data = data2[services[i]]
        #container_name = names[service_name]
        
        replicates_service = replicate_dictionary[service_name]
        
        for i in range(replicates_service):
            container_name = names[service_name]+"_"+str(i)
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

def get_childs(childs_list, data, replicas_key, default_replicas, replicate_dictionary):
    total_parents = len(data)
    for i in range(total_parents):
        childs_list.append(data[i]['service'])
        if(replicas_key in data[i]):
            print(data[i]['service'], "SIIUU")
            replicate_dictionary[data[i]['service']] = data[i][replicas_key]
        else:
            replicate_dictionary[data[i]['service']] = default_replicas
        if(len(data[i]["childrens"]) > 0):
            get_childs(childs_list,data[i]['childrens'], replicas_key, default_replicas, replicate_dictionary)

def get_id():
    # datetime object containing current date and time
    return(datetime.now().strftime("%d%m%Y%H%M%S"))

def create_env_file(alias,env_filename,environment_var_name):
    alias_string=environment_var_name+ "=" + alias+"\nCOMPOSE_DOCKER_CLI_BUILD=0"
    with open(env_filename, 'w') as f:
        f.write(alias_string)
        
    f.close()
    


def execute(request):    
    
    
    
    resultfile_location = conf['resultfile_location']
    resultfile_extension = conf['resultfile_extension']
    
    if(conf['id_stack_key'] in request and len(request[conf['id_stack_key']]) > 0):
        resultfile_id = request[conf['id_stack_key']]
    else:
        resultfile_id = get_id()
    
    if 'mode' in request:
        deploy_mode = request['mode']
    else:
        deploy_mode = 'compose'

    if 'engine' in request:
        engine = request['engine'] #nez o xelhua
    else:
        engine = 'nez'

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
    replicate_dictionary = {}
    get_childs(childs_list,request[conf['dag_key']], conf['replicas_key'], request[conf['replicas_key']], replicate_dictionary)
    print(replicate_dictionary)
    #To replicate
    childs_list = list(set(childs_list))
    
    if(conf['alias_key'] in request and len(request[conf['alias_key']]) > 0):
        alias = request[conf['alias_key']]
    else:
        alias = resultfile_id
    
    
    
    env_filename = conf['docker_envfile_location'] + conf['docker_envfile_name']    
    create_env_file(alias, env_filename, conf['environment_variable_name'])
    

    if engine=="nez":
        cfg_content = create_nez_cfgfile(resources, names, childs_list, resultfile_id, replicate_dictionary)
        resultfile_filename = os.sep.join([os.getcwd(), 'cfg-files', resultfile_id+ '.cfg'])

        f = open(resultfile_filename, "w");f.write(cfg_content);f.close()

        args = './puzzlemesh/puzzlemesh -c '+resultfile_filename+' -m ' + deploy_mode
        print(args, flush=True)
        sp = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        sp.wait()
        if sp.returncode == 0:
            print("----------------------------deployed----------------------------")
            return True,resultfile_id
        stdouterr, _ = sp.communicate()
        stdouterr = stdouterr.decode("utf-8")
        print(stdouterr)
        return False,conf['create_services_finalerror']




    if engine == "xelhua":
        docker_content = create_dockerfile(resources, names, childs_list, resultfile_id, replicate_dictionary)
        
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
            return False,e.output.decode("utf-8")
        
        services_created_array = sorted(services_created_string.split("\n"))
        print(services_created_array)
        
        try:
            command = 'docker-compose -f '+resultfile_filename+' up -d'
            os.system(command)
        except subprocess.CalledProcessError as e:
            print(e.output)
            return False,e.output.decode("utf-8")
        
        try:
            command = 'docker-compose -f '+resultfile_filename+' ps --services --filter "status=running"'
            services_running_string = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            print(e.output)
            return False,e.output.decode("utf-8")
                
        services_running_array = sorted(services_running_string.split("\n"))
        print(services_running_array)
        if(services_created_array == services_running_array):        
            return True,resultfile_id
        return False, conf['create_services_finalerror']
    