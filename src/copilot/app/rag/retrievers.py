import logging
from typing import List, Dict, Any

from rag.base import BaseRetriever
from rag.prompts import QUERY_REWRITING_PROMPT, CONTEXTUAL_COMPRESSION_PROMPT
from rag.reranker import Reranker

from schemas.document import Document, DocumentBase
from database.service import document_service

import asyncio
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    def __init__(self, retrievers: list[BaseRetriever], reranker: Reranker):
        self.retrievers = retrievers
        self.reranker = reranker

    async def get_documents(self, db, query, k, language=None, tag=None) -> List[Document]:
        """
        Retrieve documents using multiple retrievers in parallel, optionally rerank retrieved documents if a reranker is defined.

        This method executes the `get_documents` method of each retriever concurrently using asyncio.
        The results from all retrievers are aggregated into a single list, which is then returned.
        If any retriever raises an exception, it is caught and logged, but the retrieval process continues for the remaining retrievers.
        Results are reranked if a reranker is defined.
        """
        docs = []

        # Create tasks for each retriever's async get_documents method
        tasks = [
            asyncio.create_task(retriever.get_documents(db, query, k, language, tag))
            for retriever in self.retrievers
        ]

        # Gather results as they complete
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                docs.extend(result)
            except Exception as e:
                logger.exception("A retriever raised an exception during document retrieval: %s", e)

        # Remove duplicate documents based on unique 'id'
        seen = set()
        unique_docs = [doc for doc in docs if doc["id"] not in seen and not seen.add(doc["id"])]

        # Rerank the documents and get the top-k
        unique_docs, _ = await self.reranker.rerank(query, unique_docs)

        return unique_docs[:k]

class TopKRetriever(BaseRetriever):
    """
    A class used to retrieve the top K documents that semantically match a given query.

    Methods
    -------
    get_documents(db, query, language, k, language=None, tag=None)
        Retrieves the top k documents that semantically match the given query.
    """
    def __init__(self, top_k):
        self.top_k = top_k

    async def get_documents(self, db, query, k, language=None, tag=None) -> List[Document]:
        """
        Retrieves the top k documents that semantically match the given query.

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
        tag : str
            The tag of the documents to retrieve.

        Returns
        -------
        list
            A list of the top k documents that semantically match the query.
        """
        docs = await document_service.get_semantic_match(db, query, language=language, tag=tag, k=k)
        return docs[:self.top_k]

class QueryRewritingRetriever(BaseRetriever):

    def __init__(self, n_alt_queries, top_k, llm_client):
        self.n_alt_queries = n_alt_queries
        self.top_k = top_k
        self.llm_client = llm_client

    def create_query_rewriting_message(self, query: str, n_alt_queries: int = 3) -> List[Dict]:
        """
        Format the RAG message to send to the client_llm.

        Parameters
        ----------
        query : str
            User input question
        n_alt_queries: int
            Number of query rewrites to generate

        Returns
        -------
        list of dict
            Contains the message in the correct format to send to the llm_client.

        """
        query_rewriting_prompt = QUERY_REWRITING_PROMPT.format(n_alt_queries=n_alt_queries, query=query)
        return [{"role": "system", "content": query_rewriting_prompt},]

    async def rewrite_queries(self, query: str, n_alt_queries: int = 3) -> List[str]:
        """
        Rewrite the input query into multiple queries.

        This method uses the llm_client to rewrite the input query into multiple queries.
        The number of rewritten queries is specified by the parameter `n`.

        Parameters
        ----------
        query : str
            The input query to be rewritten.
        n_alt_queries : int
            The number of rewritten queries to generate, by default 3.

        Returns
        -------
        List[str]
            The list of rewritten queries.

        """
        messages = self.create_query_rewriting_message(query, n_alt_queries)
        rewritten_queries = await self.llm_client.agenerate(messages)
        rewritten_queries = rewritten_queries.choices[0].message.content.split("\n")

        return rewritten_queries

    async def get_documents(self, db, query, k, language=None, tag=None) -> List[Document]:
        """
        Retrieves the top k documents that semantically match the given original + rewritten queries.

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
        rewritten_queries = await self.rewrite_queries(query=query, n_alt_queries=self.n_alt_queries)

        docs = []
        for query in rewritten_queries:
            query_docs = await document_service.get_semantic_match(db, query, language=language, tag=tag, k=k)
            docs.extend(query_docs)

        return docs[:self.top_k]

class ContextualCompressionRetriever(BaseRetriever):

    def __init__(self, top_k, llm_client):
        self.top_k = top_k
        self.llm_client = llm_client

    def create_contextual_compression_message(self, query: str, context_doc: Document) -> List[Dict]:
        """
        Format the contextual compression message to send to the client_llm.
        """
        contextual_compression_prompt = CONTEXTUAL_COMPRESSION_PROMPT.format(context_doc=context_doc, query=query)
        return [{"role": "system", "content": contextual_compression_prompt}]

    async def compress_context(self, query: str, context_docs: List[Any]) -> List[Document]:
        # Create async tasks for each document compression
        tasks = [self.compress_doc(query, doc) for doc in context_docs]

        # Execute the tasks concurrently and gather results
        docs = await asyncio.gather(*tasks)

        # Filter out None results (for irrelevant contexts)
        return [doc for doc in docs if doc is not None]

    async def compress_doc(self, query, doc):
        messages = self.create_contextual_compression_message(query, doc)
        response = await self.llm_client.agenerate(messages)
        compressed_doc = response.choices[0].message.content

        if "<IRRELEVANT_CONTEXT>" not in compressed_doc:
            return {
                "id": doc["id"],
                "text": compressed_doc,
                "url": doc["url"],
                "language": doc["language"],
                "tag": doc["tag"]
            }
        return None

    async def get_documents(self, db, query, k, language=None, tag=None) -> List[Document]:
        """
        Retrieves the top k documents that semantically match the given query, then applies contextual compression.
        """
        docs = await document_service.get_semantic_match(db, query, language=language, tag=tag, k=k)

        # Compress the documents asynchronously
        compressed_docs = await self.compress_context(query, docs)

        # Return up to self.top_k documents
        #return compressed_docs[:self.top_k] + ([DocumentBase(text="", url="")] * (self.top_k - len(compressed_docs)))
        return compressed_docs[:self.top_k]

class RAGFusionRetriever(QueryRewritingRetriever):

    def __init__(self, llm_client, n_alt_queries: int = 3, rrf_k: int = 60, top_k: int = 10):
        self.llm_client = llm_client
        self.n_alt_queries = n_alt_queries
        self.rrf_k = rrf_k
        self.top_k = top_k

    def reciprocal_rank_fusion(self, retrieved_docs: List[List[Document]], rrf_k: int = 60):

        fused_scores = {}
        for docs in retrieved_docs:
            for rank, doc in enumerate(docs):
                if doc["id"] not in fused_scores:
                    fused_scores[doc["id"]] = {"score": 0,
                                            "text": doc["text"],
                                            "url": doc["url"],
                                            "language": doc["language"],
                                            "tag": doc["tag"]}
                fused_scores[doc["id"]]["score"] += 1 / (rank + rrf_k)

        reranked_results = [{"id": doc_id,
                             "text": doc_metadata["text"],
                             "url": doc_metadata["url"],
                             "language": doc_metadata["language"],
                             "tag": doc_metadata["tag"]} for doc_id, doc_metadata in sorted(fused_scores.items(), key=lambda x: x[1]["score"], reverse=True)]

        return reranked_results

    async def get_documents(self, db, query, k, language=None, tag=None) -> List[Document]:

        rewritten_queries = await self.rewrite_queries(query, n_alt_queries=self.n_alt_queries)

        docs = []
        for query in rewritten_queries:
            query_docs = await document_service.get_semantic_match(db, query, language=language, tag=tag, k=k)
            docs.append(query_docs)

        reranked_docs = self.reciprocal_rank_fusion(docs, rrf_k=self.rrf_k)

        return reranked_docs[:self.top_k]

class BM25Retriever(BaseRetriever):
    """
    A class used to retrieve documents based on the BM25 scoring algorithm.

    Attributes
    ----------
    k : float
        A tuning parameter that determines how the term frequency is scaled. Default is 1.2.
    b : float
        A tuning parameter that determines how the document length is scaled. Default is 0.75.
    top_k : int
        The number of top documents to retrieve. Default is 10.
    """
    def __init__(self, k: float = 1.2, b: float = 0.75, top_k: int = 10):
        self.k = k
        self.b = b
        self.top_k = top_k

    def bm25_score(self, query: str, docs: List[Any]) -> np.array:
        """
        Computes the BM25 score for each document given a query.

        Parameters
        ----------
        query : str
            The query to compute the BM25 score for.
        docs : List[Any]
            The documents to compute the BM25 score for.

        Returns
        -------
        np.array
            The BM25 scores for the documents.
        """
        # CHECK doc_len (n chars or n words)
        doc_len = np.array([len(doc.text) for doc in docs])
        avg_doc_len = np.mean(doc_len)
        n_docs = len(docs)
        freq = np.array([doc.text.count(query) for doc in docs])

        tf = np.array((freq * (1 + self.k)) / (freq + self.k * (1 - self.b + self.b * doc_len / avg_doc_len)))
        N_q = sum([1 for doc in docs if query in doc.text])
        idf = np.log(((n_docs - N_q + 0.5) / (N_q + 0.5)) + 1)

        return tf * idf

    async def get_documents(self, db, query, k, language=None, tag=None) -> List[Document]:
        """
        Retrieves the top k documents for a given query and language.

        Parameters
        ----------
        db
            The database session.
        query : str
            The query to retrieve the documents for.
        language : str
            The language of the documents to retrieve.
        k : int
            The number of documents to retrieve.

        Returns
        -------
        List[Document]
            The top k documents for the query.
        """
        docs = document_service.get_all_documents(db, tag=tag)

        # # compute bm25 score
        scores = self.bm25_score(query, docs)

        # sort retrieved context docs according to score
        top_docs = list(sorted(zip(docs, scores), key=lambda x: x[1], reverse=True))[:self.top_k]

        docs = [{"id": doc[0].id,
                 "text": doc[0].text,
                 "url": doc[0].url,
                 "language": doc[0].language,
                 "tag": doc[0].tag} for doc in top_docs]
        return docs
