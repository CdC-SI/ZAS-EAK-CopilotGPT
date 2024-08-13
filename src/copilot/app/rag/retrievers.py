from rag.base import BaseRetriever
from database.service import document_service


class TopKRetriever(BaseRetriever):

    def __init__(self):
        pass

    def get_documents(self, db, query, language, k):

        docs = document_service.get_semantic_match(db, query, language=language, k=k)
        return docs
