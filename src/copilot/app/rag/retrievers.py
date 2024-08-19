import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from rag.llm.base import BaseLLM
from rag.base import BaseRetriever
from rag.prompts import QUERY_REWRITING_PROMPT, CONTEXTUAL_COMPRESSION_PROMPT
from schemas.document import Document

from database.service import document_service

from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from cohere import Client

# Load environment variables from .env file
load_dotenv()

# Load Cohere API key
COHERE_API_KEY = os.environ["COHERE_API_KEY"]


class Reranker:

    def __init__(self, model: str, top_k: int = 10):
        self.reranking_client = Client(COHERE_API_KEY)
        self.model = model
        self.top_k = top_k

    def rerank(self, query: str, documents: List[Document]) -> List[Document]:

        reranked_docs = self.reranking_client.rerank(
            model=self.model,
            query=query,
            documents=documents,
            top_n=self.top_k,
        )

        return reranked_docs


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
    def __init__(self, retrievers: list[BaseRetriever], reranker: Reranker):
        self.retrievers = retrievers
        self.reranker = reranker

    def get_documents(self, db, query, language, k) -> List[Document]:
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
                executor.submit(retriever.get_documents, db, query, language, k): retriever
                for retriever in self.retrievers
            }

            for future in as_completed(future_to_retriever):  # Collect results as they complete
                retriever = future_to_retriever[future]
                try:
                    result = future.result()
                    docs.extend(result)
                except Exception as e:
                    print(f"Retriever {retriever} raised an exception: {e}")

        # Remove duplicate documents
        seen = set()
        unique_docs = [Document.from_orm(doc) for doc in docs if doc.id not in seen and not seen.add(doc.id)]

        if self.reranker:
            try:
                rerank_res = self.reranker.rerank(query, unique_docs).results
                rerank_idx = [res.index for res in rerank_res]
                reranked_docs = [unique_docs[i] for i in rerank_idx]
                return reranked_docs[:k]
            except Exception as e:
                print(f"Reranker raised an exception: {e}")
                return unique_docs[:k]

        return unique_docs[:k]


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

    def get_documents(self, db, query, language, k) -> List[Document]:
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

        Returns
        -------
        list
            A list of the top k documents that semantically match the query.
        """
        docs = document_service.get_semantic_match(db, query, language=language, k=k)[:self.top_k]
        return docs


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

    def rewrite_queries(self, query: str, n_alt_queries: int = 3) -> List[str]:
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
        rewritten_queries = self.llm_client.generate(messages).choices[0].message.content
        rewritten_queries = rewritten_queries.split("\n")

        return rewritten_queries

    def get_documents(self, db, query, language, k) -> List[Document]:
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
        rewritten_queries = self.rewrite_queries(query=query, n_alt_queries=self.n_alt_queries)

        docs = []
        for query in rewritten_queries:
            query_docs = document_service.get_semantic_match(db, query, language=language, k=k)
            docs.extend(query_docs)

        return docs[:self.top_k]


class ContextualCompressionRetriever(BaseRetriever):

    def __init__(self, top_k, llm_client):
        self.top_k = top_k
        self.llm_client = llm_client

    def create_contextual_compression_message(self, query: str, context_doc: Document) -> List[Dict]:
        """
        Format the contextual compression message to send to the client_llm.

        Parameters
        ----------
        query : str
            User input question
        context_doc : Document
            Context document to compress

        Returns
        -------
        list of dict
            Contains the message in the correct format to send to the llm_client.

        """
        contextual_compression_prompt = CONTEXTUAL_COMPRESSION_PROMPT.format(context_doc=context_doc, query=query)
        return [{"role": "system", "content": contextual_compression_prompt},]

    def compress_context(self, query: str, context_docs: List[Any]):
        with ThreadPoolExecutor() as executor:
            future_to_doc = {executor.submit(self.compress_doc, query, doc): doc for doc in context_docs}
            docs = []
            for future in as_completed(future_to_doc):
                result = future.result()
                if result is not None:
                    docs.append(result)
        return docs

    def compress_doc(self, query, doc):
        messages = self.create_contextual_compression_message(query, doc)
        compressed_doc = self.llm_client.generate(messages).choices[0].message.content

        if "<IRRELEVANT_CONTEXT>" not in compressed_doc:
            return Document(id=doc.id,
                            text=compressed_doc,
                            url=doc.url,
                            language=doc.language)
        return None

    def get_documents(self, db, query, language, k) -> List[Document]:
        """
        Retrieves the top k documents that semantically match the given query, then applies contextual compression.

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
        docs = document_service.get_semantic_match(db, query, language=language, k=k)
        compressed_docs = self.compress_context(query, docs)

        return compressed_docs[:self.top_k]


class RAGFusionRetriever(BaseRetriever):

    def __init__(self, llm_client, n_alt_queries: int = 3, rrf_k: int = 60, top_k: int = 10):
        self.llm_client = llm_client
        self.n_alt_queries = n_alt_queries
        self.rrf_k = rrf_k
        self.top_k = top_k

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

    def rewrite_queries(self, query: str, n_alt_queries: int = 3) -> List[str]:
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
        rewritten_queries = self.llm_client.generate(messages).choices[0].message.content
        rewritten_queries = rewritten_queries.split("\n")

        return rewritten_queries

    def reciprocal_rank_fusion(self, retrieved_docs: List[List[Document]], rrf_k: int = 60):

        fused_scores = {}
        for docs in retrieved_docs:
            for rank, doc in enumerate(docs):
                if doc.id not in fused_scores:
                    fused_scores[doc.id] = {"score": 0,
                                            "text": doc.text,
                                            "url": doc.url,
                                            "language": doc.language}
                fused_scores[doc.id]["score"] += 1 / (rank + rrf_k)

        reranked_results = [Document(id=doc_id,
                                     text=doc_metadata["text"],
                                     url=doc_metadata["url"],
                                     language=doc_metadata["language"]) for doc_id, doc_metadata in sorted(fused_scores.items(), key=lambda x: x[1]["score"], reverse=True)]

        return reranked_results

    def get_documents(self, db, query, language, k) -> List[Document]:

        rewritten_queries = self.rewrite_queries(query, n_alt_queries=self.n_alt_queries)

        docs = []
        for query in rewritten_queries:
            query_docs = document_service.get_semantic_match(db, query, language=language, k=k)
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

    def get_documents(self, db, query, language, k) -> List[Document]:
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
        docs = document_service.get_all_documents(db)

        # # compute bm25 score
        scores = self.bm25_score(query, docs)

        # sort retrieved context docs according to score
        top_docs = list(sorted(zip(docs, scores), key=lambda x: x[1], reverse=True))[:self.top_k]

        docs = [Document(id=doc[0].id,
                         text=doc[0].text,
                         url=doc[0].url,
                         language=doc[0].language) for doc in top_docs]
        return docs
