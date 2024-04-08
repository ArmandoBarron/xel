import json
import requests
import time
import logging
import getpass
import os
import inspect

class Service:

    def __init__(self,id_serv,service,params={},alias="",actions="REQUEST"):
        structure = {"id":id_serv,
         "alias":alias,
         "service":service,
         "children":[],
         "actions":[actions],
         "params":{actions:params}}
        
        self.id = id_serv
        self.status = "INIT"
        self.structure = structure
        self.message = ""

    def SetStatus(self,status,message = ""):
        self.status = status
        self.message = message
    


class DAG:
    
    def __init__(self,dag = []):
        self.task_list = []
        self.structure = dag
        self.status = "OK"

    def add_service(self,child,parent=None):

        parent_dag = None
        if parent is not None:
            parent_dag = self.LookForChildV2(parent)

        if parent_dag is not None:
            parent_dag['children'].append(child.structure)
        else:
            self.structure.append(child.structure)

        self.task_list.append(child)

    def LookForChildV2(self,task,dag = None):
        Child = None
        dag = dag if dag is not None else self.structure

        for bb in dag:
            if bb['id'] == task:
                Child = bb
                break
            else:
                if 'children' in bb:
                    Child = self.LookForChildV2(task,bb['children']) # look  by children
                else:
                    bb['children']=[]

                if Child is not None:
                    break
        return Child



class CltFunxion: #CltFunxion

    def __init__(self, base_url="http://localhost:25000",user="Guest",password="GuestP@ssword123",config_file="context.json" ):
        #constructor 
        self.user=user
        self.password=password
        self.base_url = base_url
        self.access_token = None
        self.dag = DAG()
        self.token_solution = None #token para los recursos
        self.workspace = "Default"
        self.alias =""
        self.results_dir = "./RESULTS"
        logging.basicConfig(level=logging.INFO,format='[%(asctime)s] [%(levelname)s] [%(module)s]: %(message)s')
        self.log = logging.getLogger()
        self.task_done = []
        self.force = False

        if config_file is not None:
            #si no esta vacia, osea, que tiene una ruta que cargue los datos desde el archivo txt o json
            self.load_context(config_file)

    def ForceExec(self):
        self.force = True

    def FlushTokenSolution(self):
        """
        function to generate a new token_solution 
        """
        self.token_solution=None

    def log_message(self,level, message):
        user = getpass.getuser()
        extra = {'user': user}
        
        if level == 'debug':
            self.log.debug(message, extra=extra)
        elif level == 'info':
            self.log.info(message, extra=extra)
        elif level == 'warning':
            self.log.warning(message, extra=extra)
        elif level == 'error':
            self.log.error(message, extra=extra)
        elif level == 'critical':
            self.log.critical(message, extra=extra)

    def share(self,opt="publish"):
        """
        opt :: publish,unpublish
        """

        payload = {"token_user":self.token_user,"token_solution":self.token_solution}

        
        headers = self.create_headers()

        #hacer el post a la url/deploy
        url = self.base_url+"/"+opt

        response = requests.post(url, json=payload,headers=headers)
        self.log.info(response)

        if response.status_code == 200:
            return response.json()
        else:
            return response.text

    def login(self):
        login_url = f"{self.base_url}/login"
        data = {
            "user": self.user,
            "password": self.password
        }

        response = requests.post(login_url, data=json.dumps(data))
        if response.status_code == 200:
            self.log_message("info","Login Success!")
            datos_usuario = response.json()
            self.access_token = datos_usuario['data']['access_token']
            self.token_user = datos_usuario['data']['tokenuser']
            return response.json()
            #return "Inicio de sesión exitoso."
        elif response.status_code == 401:
            return "Nombre de usuario o contraseña incorrectos."
        else:
            return "Error al iniciar sesión."

    def logout(self):
        logout_url = f"{self.base_url}/logout"
        data = {"tokenuser":self.token_user,"access_token":self.access_token}
        response = requests.post(logout_url,data=json.dumps(data))
        if response.status_code == 200:
            self.log_message("info","Logout sucess")
            return response.json()

        else:
            return "Error al cerrar sesión."

    def remove_stack(self): 
        self.log_message("info","removing containers stack!")

        data = {
            "token_solution" : self.token_solution,
            "auth":self.create_auth()
        }

        headers = self.create_headers()

        url = self.base_url+"/removestack"
        response = requests.post(url, json=data,headers=headers)
        if response.status_code == 200:
            self.log_message("info","stack deleted!")
            return response.json()
        else:
            return response.text

    def save_context(self):
        """
        guarde toda la metadata "atributos de la clase" en un archivo json, txt"
        """
        data = {
            "username" : self.user,
            "password" : self.password,
            "base_url": self.base_url,
            "token_solution": self.token_solution,
            "access_token":self.access_token
        }

        # Abre el archivo en modo escritura / esto guarda 
        with open('context.json', 'w') as archivo_json:
            json.dump(data, archivo_json)

    def load_context(self,config_file):

        if os.path.exists(config_file):
        #Cargar archivo : 
            with open(config_file, 'r') as archivo:
                contenido= json.load(archivo)

                self.user = contenido['username']
                self.password = contenido['password']
                self.base_url = contenido['base_url']
                self.token_solution = contenido['token_solution']
                self.access_token = contenido['access_token']
            self.log_message("info","context loaded")
        else:
            self.log_message("warning","No context File found")

    def create_datamap(self,filename,source="LAKE",workspace="Default"):
        """
        {data_map:{data,type},DAG:{},token_solution(optional),auth}

        type:(LAKE,SOLUTION,RECORDS,SHARED,DUMMY)

        if SOLUTION: //local transversal, detect data produced by another solution from the same user 
            {data:{token_user,token_solution,task,filename(optional)},type:SOLUTION} #un catalogo del usuario
        if RECORDS: //raw data as records 
            {data:[],type:RECORDS}
        if LAKE: //obtained from a catalog in the CDN
            {data:{token_user,catalog(workspace),filename},type:LAKE}
        if SHARED: //shared transversal, detect data produced by another solution from another user 
            {data:{shared_token,task,filename(optional)},type:SHARED} #un catalogo del usuario
        """
        self.workspace=workspace
        if source =="LAKE":
            data = {"token_user":self.token_user,"catalog":self.workspace,"filename":filename}
        if source =="DUMMY":
            data = {}

        self.data_map = {"data":data,"type":source}
        return self.data_map

    def create_headers(self):
        #crear las cookies
        headers = {
            'x-access-token': self.access_token,
            'Content-Type':'application/json'
        }
        return headers
    
    def create_auth(self):
        return {"user": self.token_user, "workspace": self.workspace}

    def deploy(self,alias=""):
        datos = {   
            "DAG":self.dag.structure,
            "auth":self.create_auth(),
            "alias":"alias"
        }
        self.alias = alias
        datos['DAG'] = json.dumps(datos["DAG"]) #DAG siempre debe ser un string
        
        if self.token_solution is not None:
             datos['token_solution']= self.token_solution 

        if self.force: #force to exec all again
            datos["options"] = {"force":"True"}

        headers = self.create_headers()

        #hacer el post a la url/deploy
        url = self.base_url+"/deploy"
        response = requests.post(url, json=datos,headers=headers)
        if response.status_code == 200:
            info_desploy = response.json()
            self.token_solution = info_desploy["token_solution"] #se guarda el nuevo token_solution
            self.log_message("info","Container's Stack created!: %s" %self.token_solution)

            return response.json()
        else:
            return response.text

    def run(self,data_map):
        datos = {   
            "DAG":self.dag.structure,
            "auth":self.create_auth(),
            "data_map":data_map,
            "alias":self.alias
        }
        
        datos['DAG'] = json.dumps(datos["DAG"]) #DAG siempre debe ser un string
        
        if self.token_solution is not None:
             datos['token_solution']= self.token_solution 

        if self.force: #force to exec all again
            datos["options"] = {"force":"True"}

        headers = self.create_headers()

        url = self.base_url+"/executeDAG"
        response = requests.post(url, json=datos,headers=headers)
        self.log_message("info","Solution is now running in background")
        self.log_message("info",response.json())

        if response.status_code == 200:
            info_exec = response.json()
            self.token_solution = info_exec["token_solution"] #se guarda el nuevo token_solution
            return response.json()
        else:
            return response.text
        
    def monitoring(self,interval_seg =1,clean_after_complete = False):
        self.task_done = []
        while True:
            time.sleep(1)
            parametros = {"kind_task":"task_list"}
            headers = self.create_headers()

            url = "%s/monitor/v2/%s/%s" %(self.base_url,self.token_user,self.token_solution)

            response = requests.post(url, json=parametros,headers=headers)
            
            self.log_message("debug",response.json())

            r_task_list = response.json()["list_task"]

            for task in self.dag.task_list:
                task_id = task.id

                if task_id in r_task_list: #
                    task.SetStatus(r_task_list[task_id]["status"],message = r_task_list[task_id]["message"] )

            #stop conditions
            
            waiting_task = []
            for task in self.dag.task_list:
                if task.status == "FINISHED" or task.status == "FAILED":
                    
                    if task.id not in self.task_done and task.status == "FINISHED": #then download results
                        self.log_message("info","%s finished succesfully!" % task.id)
                        self.GetResults(task.id)
                        self.task_done.append(task.id)
                    #download results if not exist
                        
                    #LOG MESSAGE
                    message = "[TASK %s]: %s" % (task.id,task.message)
                    self.log.error(message) if task.status =="FAILED" else self.log.info(message)
                else:
                    waiting_task.append(task.id)
            
            if len(waiting_task) == 0:
                break;
            else:
                self.log_message("info","waiting for the following task: %s" % waiting_task )

        # clean containers         
        if clean_after_complete:
            self.remove_stack()

    def validatePathIfSubtask(self,folder_name):
        if "-LVL-" in folder_name:
            if '-MAP-' in folder_name:
                folder_name = "datasets/" + folder_name

            if '-subtask-' in folder_name:
                folder_name = "products/" + folder_name

            folder_name = folder_name.replace("-VAL-","/")
            folder_name = folder_name.replace("-LVL-","/")
            folder_name = folder_name.replace("-MAP-","/")
            folder_name = folder_name.replace("-subtask-","/")
        
        return folder_name

    def createFolderIfNotExist(self,folder_name="",wd=None):

        if wd is None:
            wd = self.results_dir
        try:
            folder_name =self.validatePathIfSubtask(folder_name)
            if not os.path.exists(wd+folder_name):
                os.makedirs(wd+folder_name,0o777)
        except FileExistsError:
            pass
        return wd+folder_name

    def GetResults(self,service_id,filename=None):
        filepath_dir = self.createFolderIfNotExist("/%s/%s" % (self.token_solution,service_id)) #create solutions and service dir

        url = "%s/getfile" %(self.base_url)
        parametros = {"data":{"token_user":self.token_user,"token_solution":self.token_solution,"task":service_id},"type":"SOLUTION"} #un catalogo del usuario

        if filename is not None:
            parametros["filename"] = filename
        
        headers = self.create_headers()
        response = requests.post(url, json=parametros,headers=headers)


        # Asegúrate de que la solicitud fue exitosa
        if response.status_code == 200:
            # Obtén el nombre del archivo del header 'Content-Disposition' si está disponible
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition:
                # Extraer el nombre del archivo
                filename = content_disposition.split('filename=')[-1].strip("\"'")
            else:
                # O establece un nombre de archivo por defecto
                filename = 'downloaded_file'


            # Escribir el contenido en un archivo
            filepath = "%s/%s" % (filepath_dir,filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            self.log_message("info",f'File saved as {filename}')
        else:
            print()
            self.log_message("error",'Request error: %s ' % response.status_code)






