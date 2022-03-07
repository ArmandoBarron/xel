#functions
from Tools.Extract import ExtractData
from Tools.watcher import Watcher,Centinel
from Tools.DB_handler import Handler
import threading
from os import getenv
import logging #logger
import tarfile
import pandas as pd
import json

class Tools:

    def __init__(self,name,centinel):

        self.name = name
        self.Log = logging.getLogger()
        self.TPP_DATA= dict()
        self.TPP_RAW_DATA= dict()
        #For monitoring

        self.centinel = centinel
        if self.centinel is not None: self.centinel_status=True
        else: self.centinel_status = False
        self.dag_tps = None #static dag_tps
        self.watcher = None #instance of Watcher class:
        self.db = Handler()
        self.SCHEMAPATH= getenv('SCHEMAPATH')

    def concat(self,datasources):
        keys = list(datasources)
        S1 = datasources[keys[0]]
        S2 = datasources[keys[1]]
        merged_data = list(S1 + S2 )
        return merged_data
        
    def merge_data(self,datasources, keys_index ):
        keys = list(datasources)
        S1 = datasources[keys[0]]
        S2 = datasources[keys[1]]
        data=[]
        df1 = pd.DataFrame.from_records(S1) #pandas dataframe with all data
        df2 = pd.DataFrame.from_records(S2) #pandas dataframe with all data
        leftkeys=[]
        rightkeys=[]
        for k in keys_index:
            self.Log.error(k)
            temp = k.split("-")
            leftkeys.append(temp[0])
            rightkeys.append(temp[1])

        df = pd.merge(df1, df2, how='left', left_on=leftkeys, right_on=rightkeys)
        return json.loads(df.to_json(orient='records')) 

    def joindata(self,datasources,groupers, Arrtype="json"):
        Character= "+"
        try:
            keys = list(datasources)
            S1 = datasources[keys[0]]
            S2 = datasources[keys[1]]
            data=[]
            if Arrtype =="json":
                for Reg_S1 in S1:
                    for Reg_S2 in S2:
                        flag=True
                        for g in groupers: ## verificar que un registro cumpla con los agrupamientos
                            if(Reg_S1[g[0]]!=Reg_S2[g[1]]):
                                flag = False
                        if flag == True:
                            new_reg = dict()
                            for key1,var1 in Reg_S1.items():
                                new_reg[keys[0]+Character+key1] = var1
                            for key2,var2 in Reg_S2.items():
                                new_reg[keys[1]+Character+key2] = var2 
                            data.append(new_reg)
                            break    
            return data
        except KeyError as e:
            self.Log.error("ERROR: KEYGROUP "+ str(e) + " it's may WRONG")
            return None

    def filter_data(self,ds_data,filters):
        df = pd.DataFrame.from_records(ds_data) #pandas dataframe with all data
        if 'filters' in filters: set_filters = filters['filters']
        else: set_filters = []

        if 'columns' in filters: #select some columns
            selected_columns = filters['columns']
            df = df.filter(selected_columns)

        if 'eval' in filters: #select some columns
            evaluate = filters['eval']
            for ev in evaluate: #apply filters
                df= df.eval(ev)
        if 'rename' in filters:
            renameHeaders = filters['rename']
            for header in renameHeaders: #apply filters
                df.rename(columns=header, inplace=True)

        for flt in set_filters: #apply filters
            df= df.query(flt)

        if 'sample' in filters: #only a random sample is returned
            df= df.sample(**filters['sample'])
        
        return json.loads(df.to_json(orient='records'))

    def SplitGroups(self,GroupString):
        tpp_keygroups = GroupString.split(",")
        Groups =[]
        for group in tpp_keygroups: #KEYGROUPS
            Groups.append(group.split('-'))
        return Groups

    def create_TPP(self,jsondata):
        #keygroups = self.SplitGroups(jsondata["KEYGROUPS"])
        keygroups = jsondata["KEYGROUPS"]
        list_ds = jsondata['DS']
        dict_ds = dict()
        for ds in list_ds:
            ds_name = ds["NAME"]
            self.Log.error("++++++++++++++++++++++++++++ %s" % ds_name)

            ds_data = self.db.Get_DS_From_Workspace(self.name,ds_name)['DATA']
            if ds["Filters"] != ['']:
                self.Log.error(ds["Filters"])
                dict_ds[ds_name] = self.filter_data(ds_data,ds["Filters"]) #data filtter
            else:
                dict_ds[ds_name] =ds_data
        self.Log.warning(" ******** Data Filtered *********")
        if len(list_ds)>1:
            #we join the data using the keygroups 
            TPP_data = self.merge_data(dict_ds,keygroups)

            #TPP_data = self.joindata(dict_ds,keygroups)
            if TPP_data is None: #if there are no keygroups or these are wrong, the next option is concatenate the date as a single data
                TPP_data = self.concat(dict_ds)
        else:
            TPP_data = dict_ds[ds_name] #if is just one datasource
        self.Log.warning(" ******** TPP CREATED *********" )
        return TPP_data


    def initManager(self,DS_list): #the list of DS is send to init manager
        extractors = []
        #extracts the data using n threads (one for each datasource in the DS list)
        for ds in DS_list: #DS is a list in this case
            thread1 = threading.Thread(target = self.initExtraction, args = (ds,) )
            thread1.start()
            extractors.append(thread1)

        if self.watcher==None:
            for ex in extractors:
                ex.join()


    def initExtraction(self,DS): #is a thread. manage the extraction of data
        ds_name = DS['NAME']
        ds_watcher = DS['WATCHER']
        ds_label = DS['LABEL']
        ds_dagtp = DS['DAGTP'] #structure or reference
        try:
            workflow = DS['WORKFLOW']
        except KeyError as ke:
            raise KeyError("A workflow must be defined. if is not, define WORKFLOW: None")

        #define how the data location is going to be obtained
        if ds_watcher:
            self.Log.warning(" ------- se usara el watcher %s" % ds_dagtp)
            WCH = Watcher(ds_dagtp)
        else:
            WCH = None
        try:
            if WCH is not None:
                dag = WCH.wait_task(ds_name,workflow)
                self.Log.error(dag)
  
                DS_data = ExtractData(DS,dagtps=dag)
            else:
                DS_data = ExtractData(DS,dagtps=ds_dagtp)
            
            self.Log.warning(" ******** TPP %s data extracted *********" % ds_name)

        except ValueError as e:
                    self.Log.error("ERROR: Datasource not found,  "+ str(e))
                    self.Log.error("LOAD "+ds_name+ " FAILED" )

        if ds_label is not None:
            ds_name = ds_label

        self.db.Create_Workspace(self.name,ds_name,workflow,self.dag_tps) #create worksapce in mongo (create a DB)
        self.db.Insert_DS_in_Workspace(self.name,ds_name,DS_data)
        self.Log.warning("****** DATA "+ds_name+ " LOADED ******" )

        
    def Set_DAGtp(self,dag):
        self.dag_tps = dag

                
    def Set_Watcher(self,name):
        if self.centinel_status:
            self.watcher = self.centinel
        else:
            self.watcher = Watcher(name)

    def Get_DS(self,ds_name):
        temp =  self.db.Get_DS_From_Workspace(self.name,ds_name)
        res = dict()
        res['NAME'] = ds_name
        res['DATA'] = temp['DATA']
        res['TYPE'] = temp['TYPE']
        res['Workflow'] = temp['Workflow'] 
        return res


    def Get_all(self): #get all data sources in a Workspace
        ds_list = self.db.get_ds_names_in_workspace(self.name)
        res = dict()
        for ds in ds_list:
            if ds != 'fs.chunks'and ds != 'fs.files':
                self.Log.error(ds)
                try:
                    res[ds] = dict()
                    temp = self.db.Get_DS_From_Workspace(self.name,ds)
                    res[ds]['NAME'] = ds
                    res[ds]['DATA'] = temp['DATA']
                    res[ds]['TYPE'] = temp['TYPE']
                    res[ds]['Workflow'] = temp['Workflow']
                except Exception:
                    self.Log.error("some files have been deleted for some reason... im sorry :(")

        return res

    def Exist_DS(self,ds_name): #get all data sources in a Workspace
        ds_list = self.db.get_ds_names_in_workspace(self.name)
        if ds_name in ds_list:
            return True
        else:
            return False

    
    def LoadCollection(self,coll):
        self.name = coll['Workspace']
        self.dag_tps = coll['dag_tps']

    def toDBCollection(self):
        return {
            "Workspace":self.name,
            "DS":self.Get_all()
            }



    def Extract_from_local(self,data,path,datasource):
        with open(self.SCHEMAPATH+"/"+datasource+".tar.gz","wb") as file:
            file.write(data)
        tf = tarfile.open(self.SCHEMAPATH+"/"+datasource+".tar.gz")
        tf.extractall(self.SCHEMAPATH+"/")

        extention = path.split(".")
        if len(extention) >=2: 
            type_file = "FILE"
            DS = {"TYPE":type_file,"PATH":path,"HEADERS":"yes"}
        else:
            type_file="FOLDER"
            DS = {"TYPE":type_file,"PATH":path+"/","HEADERS":"yes"}

        ds_name = datasource
        try:
            DS_data = ExtractData(DS)
            self.Log.warning(" ******** TPP %s data extracted *********" % ds_name)
        except ValueError as e:
                    self.Log.error("ERROR: Datasource not found,  "+ str(e))
                    self.Log.error("LOAD "+ds_name+ " FAILED" )


        self.db.Create_Workspace(self.name,ds_name,"NA",self.dag_tps) #create worksapce in mongo (create a DB)
        self.db.Insert_DS_in_Workspace(self.name,ds_name,DS_data)
        self.Log.warning("****** DATA "+ds_name+ " LOADED ******" )


    def Save_DS(self,DS_data,ds_name):
        self.db.Create_Workspace(self.name,ds_name,self.name,self.dag_tps) #create worksapce in mongo (create a DB)
        self.db.Insert_DS_in_Workspace(self.name,ds_name,DS_data)
        self.Log.warning("****** DATA "+ds_name+ " LOADED ******" )
