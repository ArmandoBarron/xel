import pymongo
import os
import configparser
import logging #logger
import gridfs
from bson import json_util
from base64 import b64encode

class Handler:

    def __init__(self):
        self.dbpath = os.getenv('DATABASE') #ip for the db service
        self.Log = logging.getLogger()


    def OpenConnection(self,workspace):
        self.client = pymongo.MongoClient(self.dbpath) # defaults to port 27017
        self.db = self.client[workspace] #workflow
        self.fs = gridfs.GridFS(self.db)
        #self.db_raw = self.client.TPS_Raw_Data

        #debug
        #self.Log.warning(self.col_workspace.estimated_document_count())

    def CloseConnection(self):
        self.client.close()

    def get_ds_names_in_workspace(self,workspace):
        self.OpenConnection(workspace)
        points = self.db.collection_names()
        self.CloseConnection()
        return points


    def Create_Workspace(self,ws_name,ds_name,ds_workflow,dagtp):
        self.OpenConnection(ws_name)
        col_tpp = self.db[ds_name] #the DS in a collection
        self.delete_file_if_exist(col_tpp,ws_name)
        col_tpp.drop()
        res = col_tpp.insert(
                {
                "Workspace": ws_name,
                "DS_name":ds_name,
                "Workflow":ds_workflow,
                "DATA": '',
                "dagtp" : dagtp
                })
        self.CloseConnection()
        return res
        
    def delete_file_if_exist(self,collection,workspace):
        res = collection.find_one({'Workspace': workspace,'DATA':{'$exists': True}},{'DATA':1,'Workflow':1})
        try:
            idfile = res['DATA']
            self.fs.delete(idfile)
        except TypeError:
            pass #not exist


    def Insert_DS_in_Workspace(self,workspace,ds_name,data):
   
        self.OpenConnection(workspace)
        col_workspace = self.db[ds_name] #point
        try:
            idfile = self.fs.put(json_util.dumps(data), encoding='utf-8')
        except TypeError: #if its a binary file
            idfile = self.fs.put(data)
        self.Log.error("----------------------------------")
        self.Log.error(str(idfile))
        col_workspace.update({'Workspace': workspace},{'$set':{'DATA': idfile}})
        self.CloseConnection()
    
    def Get_DS_From_Workspace(self,workspace,ds_name):
        self.OpenConnection(workspace)
        col_workspace = self.db[ds_name] #point
        res = col_workspace.find_one({'Workspace': workspace,'DATA':{'$exists': True}},{'DATA':1,'Workflow':1} )
        idfile = res['DATA']
        self.Log.error("----------------------------------")
        data = self.fs.get(idfile)
        self.Log.error(str(idfile))

        try:
            file_data = json_util.loads(data.read()) 
            res['DATA'] = file_data
            self.Log.error(type(file_data))
            if isinstance(file_data, bytes):
                raise(TypeError)
            res['TYPE']="json"
        except TypeError: #if its a binary file
            base64_bytes = b64encode(file_data)
            res['DATA'] = base64_bytes.decode("utf-8")
            res['TYPE']="binary"
        self.CloseConnection()
        return res

