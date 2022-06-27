import os,json

with open('conf.json', 'r') as f:
        conf = json.load(f)['exe']
f.close()
def remove(id):
    file_location = conf['resultfile_location']
    file_extension = conf['resultfile_extension']
    filename = file_location + id + file_extension
    
    if(os.path.exists(filename)):
        os.system('docker-compose -f '+filename+' stop')
        os.system('docker-compose -f '+filename+' rm -f')
        os.remove(filename)
        return True        

    return False