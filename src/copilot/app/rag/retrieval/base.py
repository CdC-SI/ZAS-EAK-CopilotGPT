from typing import List
from database.models import Document
from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    @abstractmethod
    def get_documents(self, db, query, language=None, tag=None, k: int = None) -> List[Document]:
        pass
