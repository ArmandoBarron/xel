import client as c
import json
def read_data_file():
    f = open("start_services_data.json")
    data = json.load(f)
    f.close()
    return data

data = read_data_file()

c.start_services(data)

id_stack = data['id_stack']
c.remove_services(id_stack)

