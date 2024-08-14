from typing import List, Dict, Any

from rag.base import BaseRetriever
from rag.prompts import QUERY_REWRITING_PROMPT
from database.models import Document
#from rag.rag_processor import processor

from database.service import document_service

from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np


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

        return docs[:k]

class TopKRetriever(BaseRetriever):
    """
    A class used to retrieve the top K documents that semantically match a given query.

    Methods
    -------
    get_documents(db, query, language, k)
        Retrieves the top k documents that semantically match the given query.
    """
    def __init__(self, top_k):
        self.top_k = top_k

    def get_documents(self, db, query, language, k):
        """
        Retrieves the top K documents that semantically match the given query.

        Parameters
        ----------
        db : object
            The database object where the documents are stored.
        query : str
            The query to match.
        language : str
            The language of the query.
        k : int
            The number of documents to retrieve.

        Returns
        -------
        list
            A list of the top k documents that semantically match the query.
        """
        docs = document_service.get_semantic_match(db, query, language=language, k=k)[:self.top_k]
        return docs

class QueryRewritingRetriever(BaseRetriever):
    pass
    # def __init__(self, processor):
    #     self.processor = processor
    #     self.processor.stream = False

    # def create_query_rewriting_message(self, query: str, n: int = 3) -> List[Dict]:
    #     """
    #     Format the RAG message to send to the OpenAI API.

    #     Parameters
    #     ----------
    #     query : str
    #         User input question

    #     Returns
    #     -------
    #     list of dict
    #         Contains the message in the correct format to send to the OpenAI API

    #     """
    #     query_rewriting_prompt = QUERY_REWRITING_PROMPT.format(n=n, query=query)
    #     return [{"role": "system", "content": query_rewriting_prompt},]

    # def rewrite_queries(self, query: str, n: int = 3) -> List[str]:

    #     messages = self.create_query_rewriting_message(query, n)
    #     rewritten_queries = self.processor.llm_client.call(messages).choices[0].message.content
    #     rewritten_queries = rewritten_queries.split("\n")

    #     return rewritten_queries

    # def get_documents(self, db, query, language, k):

    #     rewritten_queries = self.rewrite_queries(query, n)

    #     docs = []
    #     for query in rewritten_queries:
    #         query_docs = document_service.get_semantic_match(db, query, language=language, k=k)
    #         docs.extend(query_docs)

    #     return docs

class ContextualCompressionRetriever(BaseRetriever):
    pass

class RAGFusionRetriever(BaseRetriever):
    pass

class BM25Retriever(BaseRetriever):

    def __init__(self, k: float = 1.2, b: float = 0.75, top_k: int = 10):
        self.k = k
        self.b = b
        self.top_k = top_k

    def bm25_score(self, query: str, docs: List[Any]) -> np.array:

        doc_len = np.array([len(doc.text) for doc in docs])
        avg_doc_len = np.mean(doc_len)
        n_docs = len(docs)
        freq = np.array([doc.text.count(query) for doc in docs])

        tf = np.array((freq * (1 + self.k)) / (freq + self.k * (1 - self.b + self.b * doc_len / avg_doc_len)))
        N_q = sum([1 for doc in docs if query in doc.text])
        idf = np.log(((n_docs - N_q + 0.5) / (N_q + 0.5)) + 1)

        return tf * idf

    def get_documents(self, db, query, language, k):

        docs = document_service.get_all_documents(db)

        # # compute bm25 score
        scores = self.bm25_score(query, docs)

        # # sort retrieved context docs according to score
        top_docs = list(sorted(zip(docs, scores), key=lambda x: x[1], reverse=True))[:self.top_k]

        docs = [Document(id=doc[0].id,
                         text=doc[0].text,
                         url=doc[0].url,
                         language=doc[0].language) for doc in top_docs]
        return docs

class Reranker(BaseRetriever):
    pass