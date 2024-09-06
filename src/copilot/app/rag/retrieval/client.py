from typing import List

from .reranker import Reranker
from .base import BaseRetriever
from database.models import Document

from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.logging import get_logger
logger = get_logger(__name__)


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
    get_documents(db, query, k, language=None, tag=None)
        Retrieves documents from the database using the provided query, language and returns top k documents. The results are aggregated into a single list of documents.

    """
    def __init__(self, top_k: int, retrievers: list[BaseRetriever], reranker: Reranker):
        self.top_k = top_k
        self.retrievers = retrievers
        self.reranker = reranker

    def get_documents(self, db, query, language=None, tag=None) -> List[Document]:
        """
        Retrieve documents using multiple retrievers in parallel, optionally rerank retrieved documents if a reranker is defined.

        This method executes the `get_documents` method of each retriever in parallel using a
        ThreadPoolExecutor. The results from all retrievers are aggregated into a single list,
        which is then returned. If any retriever raises an exception, it is caught and logged,
        but the retrieval process continues for the remaining retrievers. Results are reranked if a reranker is defined.

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
        tag : str
            The tag used to filter documents based on a specific category or topic.

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

        with ThreadPoolExecutor() as executor:  # Use ThreadPoolExecutor for parallel execution
            future_to_retriever = {
                executor.submit(retriever.get_documents, db, query, language, tag): retriever
                for retriever in self.retrievers
            }

            for future in as_completed(future_to_retriever):  # Collect results as they complete
                retriever = future_to_retriever[future]
                try:
                    result = future.result()
                    docs.extend(result)
                except Exception as e:
                    logger.exception(f"Retriever {retriever} raised an exception.")
                    return docs

        # Remove duplicate documents
        seen = set()
        unique_docs = [doc for doc in docs if doc.id not in seen and not seen.add(doc.id)]

        unique_docs, _ = self.reranker.rerank(query, unique_docs)

        return unique_docs[:self.top_k]
