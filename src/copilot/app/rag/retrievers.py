from rag.base import BaseRetriever
from database.service import document_service

from concurrent.futures import ThreadPoolExecutor, as_completed

class RetrieverClient(BaseRetriever):
    """
    A client for retrieving documents using multiple retrieval strategies in parallel.

    The `RetrieverClient` class manages a collection of retrievers and executes their
    `get_documents` methods in parallel, aggregating the results into a single list of documents.

    Parameters
    ----------
    retrievers : list
        A list of retriever instances that implement the `get_documents` method. These retrievers
        are executed in parallel to retrieve documents based on the specified query.

    Methods
    -------
    get_documents(db, query, language, k)
        Retrieves documents from the database using the provided query, language and returns top k documents. The results are aggregated into a single list of documents.

    """
    def __init__(self, retrievers):
        self.retrievers = retrievers

    def get_documents(self, db, query, language, k):
        """
        Retrieve documents using multiple retrievers in parallel.

        This method executes the `get_documents` method of each retriever in parallel using a
        ThreadPoolExecutor. The results from all retrievers are aggregated into a single list,
        which is then returned. If any retriever raises an exception, it is caught and logged,
        but the retrieval process continues for the remaining retrievers.

        Parameters
        ----------
        db : Any
            The database connection or session object used by the retrievers to query documents.
        query : str
            The search query used to retrieve relevant documents.
        language : str
            The language in which the documents are retrieved.
        k : int
            The number of top documents to retrieve from each retriever.

        Returns
        -------
        docs : list
            A list of documents retrieved from the database, aggregated from all the retrievers.

        Raises
        ------
        None
            Exceptions raised by individual retrievers are caught and logged, not propagated.
        """
        docs = []

        with ThreadPoolExecutor() as executor: # Use ThreadPoolExecutor for parallel execution
            future_to_retriever = {
                executor.submit(retriever.get_documents, db, query, language, k): retriever
                for retriever in self.retrievers
            }

            for future in as_completed(future_to_retriever): # Collect results as they complete
                retriever = future_to_retriever[future]
                try:
                    result = future.result()
                    docs.extend(result)
                except Exception as e:
                    print(f"Retriever {retriever} raised an exception: {e}")

        return docs

class TopKRetriever(BaseRetriever):

    def __init__(self):
        pass

    def get_documents(self, db, query, language, k):

        docs = document_service.get_semantic_match(db, query, language=language, k=k)
        return docs

class QueryRewritingRetriever(BaseRetriever):

    def __init__(self):
        pass

    def get_documents(self, db, query, language, k):

        docs = document_service.get_semantic_match(db, query, language=language, k=k)
        return docs

class ContextualCompressionRetriever(BaseRetriever):
    pass

class BM25Retriever(BaseRetriever):
    pass

class Reranker(BaseRetriever):
    pass