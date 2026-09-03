from abc import ABC, abstractmethod

class AbstractLLM(ABC):

    @abstractmethod
    def generate(self, prompt):
        pass