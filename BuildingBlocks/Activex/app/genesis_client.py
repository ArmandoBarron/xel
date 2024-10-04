import sys,json,requests


def read_json_file(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data

configuration_location = './'
configuration_filename = "conf"
configuration_extension = ".json"

configuration_path = configuration_location + configuration_filename + configuration_extension
configuration = read_json_file(configuration_path)

ss_conf = configuration['start_services']
rs_conf = configuration['remove_services']

def start_services(data):
    
    s = json.dumps(data)
    res = requests.post(ss_conf['endpoint_protocol']
                        +"://"
                        +ss_conf['endpoint_url']
                        +":"
                        +ss_conf['endpoint_port']
                        +"/"
                        +ss_conf['endpoint_name'],json=s).json()

    print(res)
    
def remove_services(id_stack):
    res = requests.post(rs_conf['endpoint_protocol']
                        +"://"
                        +rs_conf['endpoint_url']
                        +":"
                        +rs_conf['endpoint_port']
                        +"/"
                        +rs_conf['endpoint_name']
                        +"?"
                        +rs_conf['endpoint_parameters'][0]
                        +"="+
                        id_stack).json()
    print(res)