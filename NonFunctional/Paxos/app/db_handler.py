import pymongo
import os
import logging

class Handler:

    def __init__(self,db="xelhua"):
        """
        for xelhua db
            structure:: TOKEN_USER(collection) > TOKE_SOLUTION(document) 
        for xelhua_products::
            structure:: TOKE_SOLUTION(collection) > Task(document) 

        """
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
    
    def Update_one(self,collection_name,filter,update):
        client= self._openConnection()
        db = client[self.db_name] #bd
        col = db[collection_name] #the DS in a collection
        col.update_one(filter, update, upsert=True)
        self._closeConnection(client)

## more specific functions ##
    def Insert_document_if_not_exist(self,collection_name,document,query):
        client= self._openConnection()
        db = client[self.db_name] #bd
        col = db[collection_name] #the DS in a collection

        if not self.Document_exist(collection_name,document,query=query):
            res = col.insert(document)
            self.Log.info("Not existed, inserted correctly")
        else:
            self.Log.info("already exist")

        self._closeConnection(client)

        return res


    def Document_exist(self,collection_name,document,query= None):
        """
        collection name is the token user
        the document is the solution/catalog 
        """
        find_query = query if query is not None else {'token_solution': document}

        exist = False
        client= self._openConnection()
        db = client[self.db_name] #bd
        if db[collection_name].find(find_query).count() > 0:
            exist= True
        else:
            exist= False
        self._closeConnection(client)
        return exist
        

    def Get_document(self,collection_name,document,query= None):
        """
        collection name is the token user
        the document is the solution/catalog 
        """
        find_query = query if query is not None else {'token_solution':document}

        doc = {}
        client= self._openConnection()
        db = client[self.db_name] #bd
        if self.Document_exist(collection_name,document,query=query):
            doc = db[collection_name].find_one(find_query,{"_id":0 })

        self._closeConnection(client)
        return doc

    
    def List_document(self,collection_name,query={},filter_obj={"task_list":0,"_id":0 , "DAG":0,"metadata.frontend":0 }):
        """
        collection name is the token user
        """
        doc = None
        client= self._openConnection()
        db = client[self.db_name] #bd
        doc = db[collection_name].find(query,filter_obj)
        list_cur = list(doc)
        self._closeConnection(client)
        return list_cur
    
    def List_all_documents(self):
        """
        collection name is the token user
        """
        colnames = list(self.Get_all_collections())
        list_documents = []
        for col in colnames:
            documents = self.List_document(col,filter_obj={"token_solution":1, "_id":0})
            list_documents+=documents
        return list_documents
    
    
    def Delete_document(self,collection_name,document,query=None):
        """
        collection name is the token user
        the document is the solution/catalog 
        """
        find_query = query if query is not None else {'token_solution':document}

        client= self._openConnection()
        db = client[self.db_name] #bd
        if self.Document_exist(collection_name,document,query=query):
            db[collection_name].find_one_and_delete(find_query)
        self._closeConnection(client)

    def drop_db(self,db_name=None):
        try:
            db_to_drop_name = db_name if db_name is not None else self.db_name
            client= self._openConnection()
            db_to_drop = client[db_to_drop_name] #bd
            client.drop_database(db_to_drop)
            self._closeConnection(client)
        except Exception as e:
            self.Log.error("NO DB FOUND")

    def Update_document(self,collection_name,document_name,new_document,query=None):
        """
        collection name is the token user
        the document is the solution/catalog 
        insert document if not exist or update if exist
        """
        self.Delete_document(collection_name,document_name,query=query) #the old one is erased
        self.Insert_document(collection_name,new_document) #the new one is inserted

    def Insert_many(self,collection_name,list_docs):
        client= self._openConnection()
        db = client[self.db_name] #bd
        col = db[collection_name] #the DS in a collection
        try:
            col.insert_many(list_docs, ordered=False)
        except Exception as e:
            self.Log.error("SUBTASK IS AN EMPTY []")
        self._closeConnection(client)

    def Get_many_documents(self,collection_name):
        """
        collection name is the token user
        the document is the solution/catalog 
        """
        doc = {}
        client= self._openConnection()
        db = client[self.db_name] #bd
        documents = db[collection_name].find({},{"_id":0 })
        self._closeConnection(client)
        return documents
