from typing import List
from database.models import Document
from abc import ABC, abstractmethod

class BaseRetriever(ABC):
    @abstractmethod
    def get_documents(self, query: str) -> List[Document]:
        pass
