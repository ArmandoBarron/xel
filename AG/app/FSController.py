
import os
from shutil import rmtree,copy
from time import sleep
from functions import *
from base64 import b64encode,b64decode
import magic as M

class MessageController():

    def __init__(self,dag=None,token_solution=None,auth_info=None,LOGER=None):
        self.token_solution=token_solution
        self.auth=auth_info
        self.LOGER = LOGER
        self.dag = dag
        self.data_map = self.create_datamap("","")

    def create_datamap(self, path,ext):
        return {"data":path,"type":ext}
    
    def AssignDataMap(self,path,ext):
        self.data_map = self.create_datamap(path,ext)
    def GetDataMap(self):
        return self.data_map
    def GetDAG(self):
        return self.dag
    def GetAuth(self):
        return self.auth
    
    def GenerateXelRequest(self):
        return self.CreateXelRequest(self.GetDataMap(),self.GetDAG(),self.GetAuth())

    def CreateXelRequest(self,data_map,dag,auth):
        return {"data":data_map,"DAG":dag,"auth":auth}
    
class FSController():

    def __init__(self,LOGER=None,CLOUD=None,REMOTE_STORAGE=False):
        self.LOGS_FOLDER= "./LOGS/"
        createFolderIfNotExist(self.LOGS_FOLDER)
        #fh = logging.FileHandler(logs_folder+'info.log')

        #Backups folder
        self.RESULTS_FOLDER= "./BACKUPS/"
        createFolderIfNotExist(self.RESULTS_FOLDER)

        #supplies folder
        self.SPL_FOLDER= "./SUPPLIES/"
        createFolderIfNotExist(self.SPL_FOLDER)

        self.LOGER = LOGER
        self.MC = MessageController(LOGER=LOGER)

        self.CLOUD = CLOUD
        self.REMOTE_STORAGE = REMOTE_STORAGE
    
    def GetSolutionPath(self,token_solution):
        return "%s%s/" %(self.RESULTS_FOLDER,token_solution)

    def GetDataPath(self,params):
        typeOfData = params['type']
        credentials = params['data']
        try:
            if typeOfData=="RECORDS":
                input_data = pd.DataFrame.from_records(params['data']) #data is now a dataframe
                INPUT_TEMPFILE = tempfile.NamedTemporaryFile(delete=False,suffix=".csv") #create temporary file
                path= INPUT_TEMPFILE.name; INPUT_TEMPFILE.close()
                input_data.to_csv(path, index = False, header=True) #write DF to disk
            if typeOfData =="SOLUTION":
                #hay que descargar el catalogo si es necesario
                #cuando se añada SKYCDS el BKP_FOLDER se remplaza por el token del usuario
                # BKP_FOLDER = credentials['token_user']

                path = self.GetSolutionPath(credentials['token_solution'])+"/"+ validatePathIfSubtask(credentials['task']) +"/"
                if 'filename' in credentials:
                    path+=credentials['filename']
                else:
                    #tmp = os.listdir(path)
                    tmp = [f for f in os.listdir(path) if not f.startswith('.')] #ignore hidden ones
                    path +=tmp[0]
                    
            elif typeOfData=="PROJECT":
                if credentials['token_solution'] == "":
                    raise ValueError
                data_path = self.GetSolutionPath(credentials['token_solution'])+"/"
                name = "project_"+credentials['token_solution']
                ext="zip"
                path = self.GetSolutionPath(name+"."+ext)
                #LOGER.info(data_path)
                if FileExist(path):
                    pass #verify if data exist
                else:
                    path = CompressFile(self.RESULTS_FOLDER,data_path,namefile ="%s.%s"% (name,ext) )

            elif typeOfData=="LAKE":
                path = self.GetWorkspacePath(credentials['token_user'],credentials['catalog']) + credentials['filename']
            elif typeOfData=="DUMMY": #no data, just a dummy file (is the easiest way to avoid an error, sorry in advance)
                text_for_test="WAKE ME UP, BEFORE YOU GO GO.."
                INPUT_TEMPFILE = tempfile.NamedTemporaryFile(delete=False,suffix=".txt") #create temporary file
                path = INPUT_TEMPFILE.name
                INPUT_TEMPFILE.write(text_for_test.encode())
                INPUT_TEMPFILE.close()
            else:
                path="."

            name,ext = path.split("/")[-1].split(".") #get the namefile and then split the name and extention
            return path,name,ext
        except Exception as e:
            self.LOGER.error("ERROR CAUGHT trying to read the file")
            self.LOGER.error(e)
            raise(ValueError)
        
    def GetWorkspacePath(self,tokenuser,workspace=None):
        #se creara el cataloog de fuentes de datos si es que no existe
        createFolderIfNotExist("%s%s" %(self.SPL_FOLDER,tokenuser))
        if workspace is None:
            return "%s%s/" %(self.SPL_FOLDER,tokenuser)
        else:
            createFolderIfNotExist("%s%s/%s" %(self.SPL_FOLDER,tokenuser,workspace)) #create folders of user and workspace
            return "%s%s/%s/" %(self.SPL_FOLDER,tokenuser,workspace)
        
    def DeleteWorkspace(self,tokenuser,workspace=None):
        ws = self.GetWorkspacePath(tokenuser,workspace)
        rmtree(ws)
    
    def GetAllWorkspaces(self,tokenuser):
        path_workspaces= self.GetWorkspacePath(tokenuser)
        list_workspaces = [f for f in os.listdir(path_workspaces) if not f.startswith('.')] #ignore hidden ones
        return list_workspaces
    
    def GetFileWorkspace(self,tokenuser,workspace,filename):
        data_path= self.GetWorkspacePath(tokenuser,workspace)+filename
        file_exist=FileExist(data_path) #verify if data exist
        if file_exist:
            with open(data_path,"rb") as f:
                binary_data = f.read()
        else:
            binary_data = 'File not found. sorry.'.encode()
        binary_data = b64decode(binary_data)
        return binary_data

    def ListFilesWorkspace(self,tokenuser,workspace):
        path_workspace= self.GetWorkspacePath(tokenuser,workspace)
        list_of_files = [f for f in os.listdir(path_workspace) if not f.startswith('.')] #ignore hidden ones
        list_files_details = []
        for f in list_of_files:
            list_files_details.append(self.GetFileDetails(path_workspace+f,f))
        return list_files_details

    def GetFileDetails(self,filepath,filename):
        file_stats= {
            "filename":filename,
            "size":"%.2f MB" %(os.path.getsize(filepath)/(1024*1024)),
            "created at": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getctime(filepath))),
            "last modification": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(filepath))),
            "last access":time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getatime(filepath)))
        }
        return file_stats

    def GetFolder(self,fld="LOGS"):
        if fld =="LOGS":
            return self.LOGS_FOLDER
        elif fld =="DATA":
            return self.SPL_FOLDER
        elif fld =="RESULTS":
            return self.RESULTS_FOLDER
        else:
            return self.RESULTS_FOLDER
        
    def RecoverDataFromtask(self,token_solution,task):
        bkp_path = "%s%s/%s" %(self.RESULTS_FOLDER,token_solution,task)
        tmp = [f for f in os.listdir(bkp_path) if not f.startswith('.')] #ignore hidden ones
        bkp_path +="/"+tmp[0]
        ext_bk_data = bkp_path.split(".")[-1]
        self.LOGER.info("recovering data from %s ..." % bkp_path)

        return self.MC.create_datamap(bkp_path,ext_bk_data)

    def StoreFile(self,filepointer,path):
        filename = filepointer.filename
        data_path= os.path.join(path, filename)
        filepointer.save(data_path)
        return filename,data_path
        #LOGER.info(request.cookies)
    

    def verify_extentions(self,data_path,ext,response,filename,delimiter=","):
        valid = False #flag to mark a valid file
        if ext=="zip":
            valid=True
            dirpath,list_of_files=zip_extraction(data_path)
            for fname in list_of_files:
                fext = GetExtension(fname)
                response,file_validation = self.verify_extentions(dirpath+"/"+fname,fext,response,fname,delimiter) #recursive
            response['info']['tree'] = CreateFilesTree(list_of_files)
            
            # must delete the temp folder
            rmtree(dirpath)

        elif ext =="folder": #if its a folder #creo que nisiquiera se requiere
            valid=True
            list_of_files = os.listdir("%s/%s"%(data_path,filename))
            for f in list_of_files:
                fname = "%s/%s" %(filename,f)
                fext = GetExtension(fname)
                response,file_validation = self.verify_extentions(dirpath+"/"+fname,fext,response,fname,delimiter) #recursive

        elif ext=="csv":  #describe csv
            enc = detect_encode(data_path)
            #LOGER.info(enc)
            #LOGER.info(delimiter)
            dataset= pd.read_csv(data_path,encoding=enc['encoding'],sep=delimiter)
            #LOGER.info(dataset)
            response['info']['files_info'][filename] = DatasetDescription(dataset)
            response['info']['list_of_files'].append(filename)
            # normalize to utf and separated by ,
            dataset.to_csv(data_path,encoding='utf-8-sig',index=False)
            del dataset
            valid=True

        elif ext=="json":
            try:
                dataset = pd.read_json(data_path)
                response['info']['files_info'][filename] = DatasetDescription(dataset)
                valid=True
                del dataset
            except Exception as e:
                self.LOGER.error("imposible to get info")
            
            response['info']['list_of_files'].append(filename)
        else:
            response['info']['list_of_files'].append(filename)
        
        return response,valid 


    def StoreResult(self,request_obj,token_solution,task):
        tmp_f = createFolderIfNotExist("%s/" % token_solution,wd=self.RESULTS_FOLDER)
        path_to_archive= createFolderIfNotExist("%s/" % task,wd=tmp_f)
        f = request_obj.files['file']
        
        filename,file_path = self.StoreFile(f,path_to_archive)
        
        metadata = json.loads(request_obj.cookies['metadata']) if 'metadata' in request_obj.cookies else {"product_name":"product"}

        #LOGER.info(request.cookies)
        if filename == "map_metadata.json":
            metadata_folder = createFolderIfNotExist("metadata/" ,wd=tmp_f)
            copy(file_path, metadata_folder)

        if 'x-mining-statistics' in request_obj.cookies:
            name,ext = filename.split(".")
            description_filename = ".%s_desc" %(name)
            description_filepath = os.path.join(path_to_archive, description_filename)

            response={"status":"OK","message":"","file_exist":True,"info":{"parent_filename":filename,"list_of_files":[],"files_info":{}}}

            response,file_validation=self.verify_extentions(file_path,ext,response,filename,delimiter=",")
            #LOGER.info("SAVING DESC IN %s" % description_filepath)
            if file_validation: #save in file
                with open(description_filepath,'w') as f:
                    f.write(json.dumps(response))
            else:
                response['status']="ERROR"
                response['message']="Datafile can't be described. Try with the following file extentions:csv,json, or zip."

        if self.REMOTE_STORAGE:
            f.seek(0) 
            file_metadata ={}
            file_metadata['content_type'] = M.from_file(file_path, mime=True)
            token_data = CreateDataToken(token_solution,task)
            res = self.CLOUD.put(token_data,f.read(),metadata=file_metadata)

        f.close()
        del f

    def clean_results_dir(self,token_solution):
        try:
            path = self.GetSolutionPath(token_solution)
            rmtree(path)
        except FileNotFoundError:
            self.LOGER.info("dir not exist")



    def write_time_log(self,tmp,token_solution):
        f = open('%sLOG_%s.txt' % (self.LOGS_FOLDER,token_solution), 'a+');
        f.write("%s, %s, %s, %s, %s, %s, %s\n" %(tmp['id'],tmp['acq'],tmp['serv'],tmp['trans'],tmp['exec'],tmp['idx'],tmp['comm'])) 
        f.close()
        del f

    def write_solution_log(self,times,token_solution):
        with open(self.LOGS_FOLDER+'SOLUTIONS.txt', 'a+') as f: 
            f.write("%s,%s,%s,%s,%s\n" %(token_solution,times['total'],
                                        times['recovery'],
                                        times['deploy'],
                                        times['alias'] )) 