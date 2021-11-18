
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import MissingSchema
import logging
from base64 import b64decode,b64encode
import tarfile
import os.path

# Perform the communication with the TPS manager
class API:
    def __init__(self, url, workspace):
        self.base_url = url
        self.checkConnection()
        self.workspace = workspace

    # check if the service URL is valid or a service is available
    def checkConnection(self):
        """
        check if the service URL is valid or a service is available

        :raises ConnectionError: when it's not possible to connect to the URL provided
        """
        try:
            requests.head(self.base_url)
        except ConnectionError as e:
            raise ConnectionError("It is not possible connect to the URL %s" % self.base_url)
        except MissingSchema:
            raise ConnectionError("Bad URL %s" % self.base_url)

    # Extract data source
    def format_workspace(self,ws_name,ds_list):
        res = {
            "Workspace": ws_name,
            "DS":ds_list}
        return res
    
    def format_ds(self,ds_name,ds_type,dagtp,wf_name,label=None, ds_id = None, ds_headers = None, ds_path = None,watch = False):
        #if watch is True, then DAGTP has to have te reference to where is going to monitoring for the dagtp
        res = {
                "NAME": ds_name, 
                "LABEL":label,
                "TYPE": ds_type,
                "PATH": ds_path,
                "ID": ds_id,
                "WORKFLOW": wf_name,
                "WATCHER":watch,
                "DAGTP":dagtp
                }
        return res

    def format_query(self,ds1,ds2,filter1= "", filter2 = "",keygroups=""):
        query = {"DS":[
                    {"NAME":ds1, 
                    "Filters":[filter1]
                    },
                    {"NAME":ds2, 
                    "Filters":[filter2]
                    }
                ],
                "KEYGROUPS":keygroups}
        return query
    def format_single_query(self,ds1,filter1= ""):
        query = {"DS":[
                    {"NAME":ds1, 
                    "Filters":filter1
                    }
                ],
                "KEYGROUPS":""}
        return query

    def LoadData(self, jsonData):
        """
        Load DAGtps to TPS manager

        :param dagtps: :class: json object to save
        :type dagtps: :class: json

        :param tpp: :class: json object with transversal points
        :type tpp: :class: json

        :raises Exception: when dagtps or tpp are in a diferent format
        """
    
        service = "/extract"
        url = self.base_url + service
        res = requests.put(url, json=jsonData)
        if res.status_code == 201:  # created
            return "OK"
        else:
            raise Exception("Load error, key error (keygroup) %d %s" % (res.status_code, res.reason))

    # get Data from a TPP or a TPP/DS
    def GetData(self,DS,workspace=None):
        """
        aReturn the data inside a TPP in json format

        :param TPP: name of the TPP for data extract 
        :type workflow_id: string

        :param DS: optional DS inside the TPP
        :type DS: string

        :raises Exception: when there is an error with the call
        """
        if workspace is None: workspace = self.workspace
        service = "/%s/%s" % (workspace, DS)
        url = self.base_url + service
        res = requests.get(url)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong %d %s" % (res.status_code, res.reason))
        else:
            data = res.json()
            if data["TYPE"] == "binary":
                data["DATA"] = b64decode(data["DATA"].encode())
            return data

    def make_tarfile(self,output_filename, source_dir):
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
            
    def PutData(self,path,label,workspace=None):
        """
        Send data found in a local path (file or folder)

        :param path: location in file system 
        :type: string

        :raises Exception: when there is an error with the call
        """
        if workspace is None: workspace = self.workspace

        self.make_tarfile("data_dump.tar.gz",path)
        path_name = path.split("/")[-1]
        with open("data_dump.tar.gz", mode='rb') as file: # read tar file
            fileContent = file.read()
            base64_bytes = b64encode(fileContent)
            data = {"data":base64_bytes.decode("utf-8"),"path":path_name}

        service = "/%s/putdata/%s/" % (workspace,label) 
        url = self.base_url + service
        res = requests.put(url, json = data)
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong %d %s" % (res.status_code, res.reason))
        else:
            return res.json()

    ########################################################################################
    ###############################     SERVICES     #######################################
    ########################################################################################

    def TPS(self, query,service_name,options = None, workload=None, workspace=None,label = None):
        """
        Transversal processing service call

        :param query: dictionari with dataset specifications (use format_query() function)
        :type query: dict()

        :param service_name: TPS name
        :type service_name: string

        :param options: Set of TPS options
        :type options: Dict

        :param label: Name of the DS to save results in manager DB. (None by default, the results are going to be retrive by the fucntion )
        :type options: Dict


        :raises Exception: when there is an error with the call
        """
        self.checkConnection()
        if workspace is None: workspace = self.workspace
        data = {"query":query,"options":options,"label":label}

        if workload is not None: data['workload'] = workload

        service = "/%s/TPS/%s" % (workspace,service_name)
        url = self.base_url + service
        res = requests.post(url, json = data)
       
        if res.status_code != 201 and res.status_code != 200:  # error
            raise Exception("Something went wrong %d %s" % (res.status_code, res.reason))
        else:
            res = res.json()
            if 'TYPE' in res:
                if res["TYPE"] == "binary":
                    try:
                        res["result"] = b64decode(res["result"].encode())
                    except AttributeError:
                        #maybe its a dict
                        res["result"] = res["result"]
            return res

