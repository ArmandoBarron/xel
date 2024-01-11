import json
import requests

class CltFunxion: #CltFunxion

    
    def __init__(self, base_url,user,password,config_file=None ):

        #constructor 
        self.user=user
        self.password=password
        self.base_url = base_url
        self.token_solution = None #token para los recursos

        if config_file is not None:
            #si no esta vacia, osea, que tiene una ruta que cargue los datos desde el archivo txt o json
            pass

    def login(self):
            login_url = f"{self.base_url}/login"
            data = {
                "user": self.user,
                "password": self.password
            }
            #print(login_url)
            response = requests.post(login_url, data=json.dumps(data))
            #print(response)
            if response.status_code == 200:
                print("Inicio de sesión existoso")
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
            print(response.text)
            if response.status_code == 200:
                return response.json()
            else:
                return "Error al cerrar sesión."

    def reset_resources(self):
        self.token_solution = None

    
    def remove_stack(self,access_token): 

        data = {
            "token_solution" : self.token_solution,
        }

        response = requests.post(self.base_url , data=data)

        if response.status_code==200:

            print("Solicitud Existosa ")

        else:
            print(" Error en la solicitud ")



    def save_context(self):
        """
        guarde toda la metadata "atributos de la clase" en un archivo json, txt"
        """
        data = {
            "username" : self.user,
            "password" : self.password,
            "base_url ": self.base_url,
            "token_solution": self.token_solution
        }

        # Abre el archivo en modo escritura / esto guarda 
        with open('context.json', 'w') as archivo_json:
            json.dump(data, archivo_json)

        
    def load_context(self):

         #Cargar archivo : 
        with open('context.json', 'r') as archivo:
            contenido= json.load(archivo)

            self.user = contenido['username']
            #hacer lo mismo para todas las demas


        print(contenido)
            


    def deploy (self,token_user,access_token,service="funxion"):
        datos = {   
            "DAG":[{"id":"ALGO","alias":"ALGO unico","service":service,"childrens":[],"actions":[""],"params":{}}],
            "auth":{"user": token_user, "workspace": "Default"},
            "alias":"Funxion"
        }
        datos['DAG'] = json.dumps(datos["DAG"]) #DAG siempre debe ser un string
        
        if self.token_solution is not None:
             datos['token_solution']= self.token_solution 

        #crear las cookies
        headers = {
            'x-access-token': access_token,
            'Content-Type':'application/json'
        }
        #hacer el post a la url/deploy
        url = self.base_url+"/deploy"
        response = requests.post(url, json=datos,headers=headers)
        if response.status_code == 200:
            info_desploy = response.json()
            self.token_solution = info_desploy["token_solution"] #se guarda el nuevo token_solution
            return response.json()
        else:
            return response.text


        
    


if __name__ == "__main__":
    base_url = "http://localhost:25000"  

    username = "Betza"
    password = "Betza123"
    Objeto = CltFunxion(base_url,username,password)
    datos_acceso = Objeto.login()
    print(datos_acceso['data']['access_token'])
    print(Objeto.logout())
    datos_acceso = Objeto.login()
    print(datos_acceso['data'])
    access_token = datos_acceso['data']['access_token']
    token_user = datos_acceso['data']['tokenuser']
    deploy_info = Objeto.deploy(token_user=token_user,access_token=access_token,service="charts")
    remove_stack_info = Objeto.remove_stack(token_user=token_user,access_token=access_token)



    #Objeto.save_context()
    #print(deploy_info)

    exit(1)



