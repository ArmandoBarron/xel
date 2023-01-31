import os,json
import glob
import logging

logging.basicConfig(level=logging.INFO)

LOGER = logging.getLogger()

with open('conf.json', 'r') as f:
        conf = json.load(f)['exe']
f.close()
def remove(id):
    file_location = conf['resultfile_location']
    file_extension = conf['resultfile_extension']
    filename = file_location + id + file_extension
    
    file_location_nez = os.getenv("HOST_PATH")+"results/"+id+"/docker-compose.yml"
    dir_location_nez = os.getenv("HOST_PATH")+"results/"

    #esto remueve para el modulo de xelhua
    if(os.path.exists(filename)):
        os.system('docker-compose -f '+filename+' stop')
        os.system('docker-compose -f '+filename+' rm -f')
        os.remove(filename)
        return True   

    if(os.path.exists(file_location_nez)):
        matching_folders = glob.glob(dir_location_nez+"*"+id+"*")
        for matching_folder in matching_folders:
            file_location = matching_folder+"/docker-compose.yml"
            #LOGER.error(file_location)
            os.system('docker-compose -p '+matching_folder+' -f '+file_location+' stop')
            os.system('docker-compose -p '+matching_folder+' -f '+file_location+' down')
        return True
    return False