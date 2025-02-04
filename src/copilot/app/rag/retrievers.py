from abc import ABC, abstractmethod
import logging
from typing import List, Any

from rag.reranker import Reranker

from schemas.document import Document
from database.service import document_service

import asyncio
import numpy as np

from langfuse.decorators import observe

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BaseRetriever(ABC):
    @abstractmethod
    def get_documents(
        self,
        db,
        query,
        k,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:
        pass


class RetrieverClient(BaseRetriever):
    """
    A client for retrieving documents using multiple retrieval strategies in parallel.

    The `RetrieverClient` class manages a collection of retrievers and executes their
    `get_documents` methods asynchronously, aggregating the results into a single list of documents.
    """

    def __init__(self, retrievers: list[BaseRetriever], reranker: Reranker):
        self.retrievers = retrievers
        self.reranker = reranker

    @observe(name="RetrieverClient")
    async def get_documents(
        self,
        db,
        query,
        k_retrieve,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:
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
            asyncio.create_task(
                retriever.get_documents(
                    db=db,
                    query=query,
                    k=k_retrieve,
                    language=language,
                    tags=tags,
                    source=source,
                    organizations=organizations,
                    user_uuid=user_uuid,
                    **kwargs,
                )
            )
            for retriever in self.retrievers
        ]

        # Gather results as they complete
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                docs.extend(result)
            except Exception as e:
                logger.exception(
                    "A retriever raised an exception during document retrieval: %s",
                    e,
                )

        # Remove duplicate documents based on unique 'id'
        seen = set()
        unique_docs = [
            doc
            for doc in docs
            if doc["id"] not in seen and not seen.add(doc["id"])
        ]

        # Rerank the documents and get the top-k
        if unique_docs and self.reranker:
            unique_docs, _ = await self.reranker.rerank(
                query,
                unique_docs,
            )

        logger.info("Retrieved %d documents", len(unique_docs[:k_retrieve]))

        return unique_docs[:k_retrieve]


class TopKRetriever(BaseRetriever):
    """
    A class used to retrieve the top K documents that semantically match a given query.
    """

    def __init__(self, top_k):
        self.top_k = top_k

    @observe(name="TopKRetriever_get_documents")
    async def get_documents(
        self,
        db,
        query,
        k,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:
        """
        Retrieves the top k documents that semantically match the given query.
        Ignores any extra kwargs not needed by this retriever.
        """
        docs = await document_service.get_semantic_match(
            db,
            query,
            language=language,
            tags=tags,
            source=source,
            organizations=organizations,
            user_uuid=user_uuid,
            k=k,
            embedding_field="text_embedding",
        )
        return docs[: self.top_k]


class QueryRewritingRetriever(BaseRetriever):

    def __init__(self, n_alt_queries, top_k, llm_client, message_builder):
        self.n_alt_queries = n_alt_queries
        self.top_k = top_k
        self.llm_client = llm_client
        self.message_builder = message_builder

    @observe(name="QueryRewritingRetriever_rewrite_queries")
    async def rewrite_queries(
        self, language: str, llm_model: str, query: str, n_alt_queries: int = 3
    ) -> List[str]:
        """
        Rewrite the input query into multiple query variations (variations, declarative).
        This method uses the llm_client to rewrite the input query into multiple queries.
        The number of rewritten queries (total: 2*n_alt_queries) is specified by the parameter `n_alt_queries`.
        """
        # Query reformulations (variations)
        messages = self.message_builder.build_query_rewriting_prompt(
            language, llm_model, n_alt_queries, query
        )
        rewritten_queries = await self.llm_client.agenerate(messages)
        rewritten_queries = rewritten_queries.choices[0].message.content.split(
            "\n"
        )

        # Query reformulations (declarative)
        messages = self.message_builder.build_query_statement_rewriting_prompt(
            language, llm_model, n_alt_queries, query
        )
        rewritten_declarative_queries = await self.llm_client.agenerate(
            messages
        )
        rewritten_declarative_queries = rewritten_declarative_queries.choices[
            0
        ].message.content.split("\n")

        reformulated_queries = (
            rewritten_queries + rewritten_declarative_queries
        )
        return reformulated_queries

    @observe(name="QueryRewritingRetriever_get_documents")
    async def get_documents(
        self,
        db,
        query,
        k,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:
        """
        Retrieves the top k documents that semantically match the given original + rewritten queries.
        """
        llm_model = kwargs.get("llm_model", "gpt-4o-mini")
        rewritten_queries = await self.rewrite_queries(
            language, llm_model, query=query, n_alt_queries=self.n_alt_queries
        )

        # Execute all semantic matching operations concurrently
        tasks = [
            document_service.get_semantic_match(
                db,
                query,
                language=language,
                tags=tags,
                source=source,
                organizations=organizations,
                user_uuid=user_uuid,
                k=k,
                embedding_field="text_embedding",
            )
            for query in rewritten_queries
        ]
        results = await asyncio.gather(*tasks)

        # Flatten the list of results
        docs = [doc for result in results for doc in result]

        return docs[: self.top_k]


class ContextualCompressionRetriever(BaseRetriever):

    def __init__(self, top_k, llm_client, message_builder):
        self.top_k = top_k
        self.llm_client = llm_client
        self.message_builder = message_builder

    async def compress_context(
        self,
        language: str,
        llm_model: str,
        query: str,
        context_docs: List[Any],
    ) -> List[Document]:
        # Create async tasks for each document compression
        tasks = [
            self.compress_doc(language, llm_model, query, doc)
            for doc in context_docs
        ]

        # Execute the tasks concurrently and gather results
        docs = await asyncio.gather(*tasks)

        # Filter out None results (for irrelevant contexts)
        return [doc for doc in docs if doc is not None]

    @observe(name="ContextualCompressionRetriever_compress_doc")
    async def compress_doc(self, language, llm_model, query, doc):
        messages = self.message_builder.build_contextual_compression_prompt(
            language, llm_model, doc["text"], query
        )
        response = await self.llm_client.agenerate(messages)
        compressed_doc = response.choices[0].message.content

        if "<IRRELEVANT_CONTEXT>" not in compressed_doc:
            return {
                "id": doc["id"],
                "text": compressed_doc,
                "url": doc["url"],
                "language": doc["language"],
                "tags": doc["tags"],
            }
        return None

    @observe(name="ContextualCompressionRetriever_get_documents")
    async def get_documents(
        self,
        db,
        query,
        k,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:
        """
        Retrieves the top k documents that semantically match the given query, then applies contextual compression.
        """
        llm_model = kwargs.get("llm_model", "gpt-4o-mini")

        docs = await document_service.get_semantic_match(
            db,
            query,
            language=language,
            tags=tags,
            source=source,
            organizations=organizations,
            user_uuid=user_uuid,
            k=k,
            embedding_field="text_embedding",
        )

        # Compress the documents asynchronously
        compressed_docs = await self.compress_context(
            language, llm_model, query, docs
        )

        # Return up to self.top_k documents
        # return compressed_docs[:self.top_k] + ([DocumentBase(text="", url="")] * (self.top_k - len(compressed_docs)))
        return compressed_docs[: self.top_k]


class RAGFusionRetriever(QueryRewritingRetriever):

    def __init__(
        self,
        llm_client,
        message_builder,
        n_alt_queries: int = 3,
        rrf_k: int = 60,
        top_k: int = 10,
    ):
        super().__init__(n_alt_queries, top_k, llm_client, message_builder)
        self.rrf_k = rrf_k

    @observe(name="RAGFusionRetriever_reciprocal_rank_fusion")
    def reciprocal_rank_fusion(
        self, retrieved_docs: List[List[Document]], rrf_k: int = 60
    ):

        fused_scores = {}
        for docs in retrieved_docs:
            for rank, doc in enumerate(docs):
                if doc["id"] not in fused_scores:
                    fused_scores[doc["id"]] = {
                        "score": 0,
                        "text": doc["text"],
                        "url": doc["url"],
                        "language": doc["language"],
                        "tags": doc["tags"],
                    }
                fused_scores[doc["id"]]["score"] += 1 / (rank + rrf_k)

        reranked_results = [
            {
                "id": doc_id,
                "text": doc_metadata["text"],
                "url": doc_metadata["url"],
                "language": doc_metadata["language"],
                "tags": doc_metadata["tags"],
            }
            for doc_id, doc_metadata in sorted(
                fused_scores.items(), key=lambda x: x[1]["score"], reverse=True
            )
        ]

        return reranked_results

    @observe(name="RAGFusionRetriever_get_documents")
    async def get_documents(
        self,
        db,
        query,
        k,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:

        llm_model = kwargs.get("llm_model", "gpt-4o-mini")

        rewritten_queries = await self.rewrite_queries(
            language, llm_model, query, n_alt_queries=self.n_alt_queries
        )

        docs = []
        for query in rewritten_queries:
            query_docs = await document_service.get_semantic_match(
                db,
                query,
                language=language,
                tags=tags,
                source=source,
                organizations=organizations,
                user_uuid=user_uuid,
                k=k,
                embedding_field="text_embedding",
            )
            docs.append(query_docs)

        reranked_docs = self.reciprocal_rank_fusion(docs, rrf_k=self.rrf_k)

        return reranked_docs[: self.top_k]


class BM25Retriever(BaseRetriever):
    """
    A class used to retrieve documents based on the BM25 scoring algorithm.
    """

    def __init__(self, k: float = 1.2, b: float = 0.75, top_k: int = 10):
        self.k = k
        self.b = b
        self.top_k = top_k

    def bm25_score(self, query: str, docs: List[Any]) -> np.array:
        """
        Computes the BM25 score for each document given a query.
        """
        # CHECK doc_len (n chars or n words)
        doc_len = np.array([len(doc.text) for doc in docs])
        avg_doc_len = np.mean(doc_len)
        n_docs = len(docs)
        freq = np.array([doc.text.count(query) for doc in docs])

        tf = np.array(
            (freq * (1 + self.k))
            / (freq + self.k * (1 - self.b + self.b * doc_len / avg_doc_len))
        )
        N_q = sum([1 for doc in docs if query in doc.text])
        idf = np.log(((n_docs - N_q + 0.5) / (N_q + 0.5)) + 1)

        return tf * idf

    @observe(name="BM25Retriever_get_documents")
    async def get_documents(
        self,
        db,
        query,
        k,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:
        """
        Retrieves the top k documents for a given query and language.
        Ignores any extra kwargs not needed by this retriever.
        """
        docs = document_service.get_all_documents(db, tags=tags, source=source)

        # # compute bm25 score
        scores = self.bm25_score(query, docs)

        # sort retrieved context docs according to score
        top_docs = list(
            sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        )[: self.top_k]

        docs = [
            {
                "id": doc[0].id,
                "text": doc[0].text,
                "url": doc[0].url,
                "language": doc[0].language,
                "tags": doc[0].tags,
            }
            for doc in top_docs
        ]
        return docs


class TrigramRetriever(BaseRetriever):
    pass


class SemanticMetadataRetriever(TopKRetriever):
    """
    A subclass of TopKRetriever that matches the embedded query against multiple embeddings fields.
    """

    EMBEDDING_FIELDS = [
        "summary_embedding",
        "tags_embedding",
        "subtopics_embedding",
        "hyq_embedding",
        "hyq_declarative_embedding",
    ]

    def __init__(self, top_k):
        super().__init__(top_k)

    @observe(name="SemanticMetadataRetriever_get_documents")
    async def get_documents(
        self,
        db,
        query,
        k,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:
        """
        Retrieves documents by matching against multiple embedding fields concurrently.
        """
        docs = await document_service.get_semantic_match(
            db,
            query,
            language=language,
            tags=tags,
            source=source,
            organizations=organizations,
            user_uuid=user_uuid,
            k=k,
            embedding_field=self.EMBEDDING_FIELDS,
        )

        return docs[: self.top_k]


class FedlexRetriever(TopKRetriever):
    """
    A class used to retrieve documents with "fedlex" source.
    Also checks the art.1 (application/applicability) of the law upon which each document is based.
    """

    def __init__(self, top_k):
        super().__init__(top_k)

    @observe(name="FedlexRetriever_get_documents")
    async def get_documents(
        self,
        db,
        query,
        k,
        language=None,
        tags=None,
        source=None,
        organizations=None,
        user_uuid=None,
        **kwargs
    ) -> List[Document]:
        """
        Retrieves documents by matching against multiple embedding fields concurrently,
        but only from fedlex source.
        """
        return await super().get_documents(
            db=db,
            query=query,
            k=k,
            language=language,
            tags=tags,
            source=["fedlex"],
            organizations=organizations,
            user_uuid=user_uuid,
            **kwargs,
        )


class ContextualRagRetriever(BaseRetriever):
    pass


class RaptorRetriever(BaseRetriever):
    pass


class GraphRagRetriever(BaseRetriever):
    pass


class LightRagRetriever(BaseRetriever):
    pass
