from rag.base import BaseRetriever
from database.service import document_service


class SimpleRetriever(BaseRetriever):

    def __init__(self):
        pass

    def get_documents(self, db, query, language, k):

        print("-----------------ROWS: ", document_service.get_semantic_match(db, query, language, k))
        return document_service.get_semantic_match(db, query, language, k)
