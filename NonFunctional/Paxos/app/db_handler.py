import pymongo
import os
import logging

class Handler:

    def __init__(self,db="xelhua"):
        self.db_host = os.getenv('DATABASE_HOST') #ip for the db service
        self.Log = logging.getLogger()
        self.db_name=db

    def _openConnection(self):
        client = pymongo.MongoClient(self.db_host) # defaults to port 27017
        return client

    def _closeConnection(self,client):
        client.close()

    def Get_all_collections(self):
        client= self._openConnection()
        db = client[self.db_name] #bd
        result = db.collection_names()
        self._closeConnection(client)
        return result

    def Insert_document(self,collection_name,document):
        client= self._openConnection()
        db = client[self.db_name] #bd
        col = db[collection_name] #the DS in a collection
        res = col.insert(document)
        self._closeConnection(client)
        return res

## more specific functions ##

    def Document_exist(self,collection_name,token_solution):
        """
        collection name is the token user
        the document is the solution/catalog 
        """
        exist = False
        client= self._openConnection()
        db = client[self.db_name] #bd
        if db[collection_name].find({'token_solution': token_solution}).count() > 0:
            exist= True
        else:
            exist= False
        self._closeConnection(client)
        return exist
        

    def Get_document(self,collection_name,token_solution):
        """
        collection name is the token user
        the document is the solution/catalog 
        """
        doc = {}
        client= self._openConnection()
        db = client[self.db_name] #bd
        if self.Document_exist(collection_name,token_solution):
            doc = db[collection_name].find_one({'token_solution':token_solution},{"_id":0 })

        self._closeConnection(client)
        return doc

    
    def List_document(self,collection_name):
        """
        collection name is the token user
        """
        doc = None
        client= self._openConnection()
        db = client[self.db_name] #bd
        doc = db[collection_name].find({},{"task_list":0,"_id":0 , "DAG":0,"metadata.frontend":0 })
        list_cur = list(doc)
        self._closeConnection(client)
        return list_cur
    
    def Delete_document(self,collection_name,token_solution):
        """
        collection name is the token user
        the document is the solution/catalog 
        """
        client= self._openConnection()
        db = client[self.db_name] #bd
        if self.Document_exist(collection_name,token_solution):
            db[collection_name].find_one_and_delete({'token_solution':token_solution})
        self._closeConnection(client)


    def Update_document(self,collection_name,token_solution,new_document):
        """
        collection name is the token user
        the document is the solution/catalog 
        insert document if not exist or update if exist
        """
        self.Delete_document(collection_name,token_solution) #the old one is erased
        self.Insert_document(collection_name,new_document) #the new one is inserted
