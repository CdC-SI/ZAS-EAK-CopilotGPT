from typing import List
from database.models import Document
from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    @abstractmethod
    def get_documents(self, db, query, k, language=None, tag=None) -> List[Document]:
        pass

class BaseRouter(ABC):
    def __init__(self):
        self.encoder = None
        self.routes = None

    def load_routes(self):
        pass