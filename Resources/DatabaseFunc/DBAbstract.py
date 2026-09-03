from abc import ABC,abstractmethod
class AbrtractDatabaseController(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def insert(self):
        pass

    @abstractmethod
    def find(self):
        pass

    @abstractmethod
    def delete(self):
        pass
    

    @abstractmethod
    def insert_multiple(self):
        pass

    @abstractmethod
    def find_multiple(self):
        pass

    @abstractmethod
    def delete_multiple(self):
        pass

    @abstractmethod
    def alter(self):
        pass

    

