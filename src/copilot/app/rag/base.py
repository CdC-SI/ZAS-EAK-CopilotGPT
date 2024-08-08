from abc import ABC, abstractmethod

class BaseRetriever(ABC):
    @abstractmethod
    def get_documents(self):
        pass
