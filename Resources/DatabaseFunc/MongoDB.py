from .DBAbstract import AbstractDatabaseController
from pymongo import MongoClient
from pymongo.errors import ConfigurationError

class MongoDBController(AbstractDatabaseController):
    def __init__(self, collection, uri="mongodb://localhost:27017", db_name:str|None=None):
        self.uri = uri
        self.db_name = db_name
        self.collection=collection
 
    def connect(self):
        self.client = MongoClient(self.uri,serverSelectionTimeoutMS=5000) 
        self.client.admin.command("ping")
        if self.db_name: self.db = self.client[self.db_name]
        else: 
            try:
                self.db = self.client.get_default_database()  # db from URI path
            except ConfigurationError:
                raise ValueError("Pass db_name or include a database in the URI")

 
    def close(self):
        if self.client:
            self.client.close()
            self.client = self.db = None
 
    def insert(self, record):
        return self.db[self.collection].insert_one(record).inserted_id
 
    def insert_multiple(self, records):
        return self.db[self.collection].insert_many(records).inserted_ids
 
    def find(self, query=None):
        return list(self.db[self.collection].find(query or {}))
 
    def update(self, query, changes):
        return self.db[self.collection].update_many(query, {"$set": changes}).modified_count
 
    def delete(self, query):
        return self.db[self.collection].delete_many(query).deleted_count