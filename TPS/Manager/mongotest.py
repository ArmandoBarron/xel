import pymongo

client = pymongo.MongoClient("mongodb://Admin:TPSAdmin@10.113.83.84/TPP_data") # defaults to port 27017

db = client.TPP_data

# print the number of documents in a collection
print (db.TPP_data.estimated_document_count())