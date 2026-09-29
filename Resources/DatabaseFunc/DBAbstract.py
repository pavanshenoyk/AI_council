from abc import ABC,abstractmethod
class AbstractDatabaseController(ABC):
    @abstractmethod
    def connect(self): ...
 
    @abstractmethod
    def close(self): ...
 
    @abstractmethod
    def insert(self, collection, record): ...
 
    @abstractmethod
    def find(self, collection, query): ...
 
    @abstractmethod
    def update(self, collection, query, changes): ...
 
    @abstractmethod
    def delete(self, collection, query): ...
 
    def insert_multiple(self, collection, records):
        return [self.insert(collection, r) for r in records]

