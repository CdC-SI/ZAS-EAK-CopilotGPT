from abc import ABC, abstractmethod


class BaseRetriever(ABC):
    @abstractmethod
    def get_documents(self, db, query, language, k):
        pass
