from .DBAbstract import AbstractDatabaseController
from pymongo import MongoClient

class MongoDBController(AbstractDatabaseController):
    def __init__(self, uri="mongodb://localhost:27017", db_name="app"):
        self.uri = uri
        self.db_name = db_name
 
    def connect(self):
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
 
    def close(self):
        self.client.close()
 
    def insert(self, collection, record):
        return self.db[collection].insert_one(record).inserted_id
 
    def insert_multiple(self, collection, records):
        return self.db[collection].insert_many(records).inserted_ids
 
    def find(self, collection, query=None):
        return list(self.db[collection].find(query or {}))
 
    def update(self, collection, query, changes):
        return self.db[collection].update_many(query, {"$set": changes}).modified_count
 
    def delete(self, collection, query):
        return self.db[collection].delete_many(query).deleted_count