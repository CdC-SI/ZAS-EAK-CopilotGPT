from typing import Optional
from dataclasses import asdict

from .client import RetrieverClient
from .retrievers import Retrievers
from .reranker import Reranker
from .base import BaseRetriever

from utils.enum import VectorMetric

from config.rag import retrievers as config
from config.rag.retrieval import RerankingConfig

import logging
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RetrieverFactory:
    """
    A factory class for creating a RetrieverClient based on the specified retrieval methods.

    This factory method allows for the creation of a composite retriever client that can use multiple
    retrieval strategies in sequence or in parallel, depending on the specified methods.

    Methods
    -------
    get_retriever_client(retrieval_method: str) -> RetrieverClient
        Creates a RetrieverClient instance configured with the specified retrieval methods.

    """
    @staticmethod
    def get_retriever_client(top_k: int, metric: VectorMetric, retrievers: list[dict], Reranking: Optional[dict] = None) -> RetrieverClient:
        """
        Create a RetrieverClient based on the given retrieval method(s).

        Parameters
        ----------
        top_k : int
            The number of documents to retrieve.
        metric : VectorMetric
            The metric to use for ranking the retrieved documents
        retrievers : list[dict]
            A list of dict specifying the retrieval methods to use and their parameters.
        Reranking : RerankingConfig

        Returns
        -------
        RetrieverClient
            A RetrieverClient instance configured with the specified retrieval methods.

        Raises
        ------
        ValueError
            If an unsupported retrieval method is provided.
        """
        reranker = None
        if Reranking:
            if not isinstance(Reranking, dict):
                Reranking = asdict(RerankingConfig())
            reranker = Reranker(**Reranking)
            logger.info(f"Adding a reranker: {Reranking}")

        all_retrievers = RetrieverFactory.get_retrievers(retrievers)

        client = RetrieverClient(top_k=top_k, retrievers=all_retrievers, reranker=reranker)
        return client

    @staticmethod
    def get_retrievers(retrievers: list[dict]) -> list[BaseRetriever]:
        """
        Create a list of retrievers based on the given retrieval method(s).

        Parameters
        ----------
        retrievers : list[str] or list[config.Retriever]
            A string or a list of strings or configuration items specifying the retrieval methods to use.
            Supported methods are specified in the `Retrievers` enum.

        Returns
        -------
        list[BaseRetriever]
            A list of retrievers configured with the specified retrieval methods.
        """
        all_retrievers = []

        for retriever in retrievers:
            logger.info(f"Adding a retriever: {retriever}")
            if isinstance(retriever, dict):
                all_retrievers.append(Retrievers[retriever.pop('type_').name].value(**retriever))
            elif isinstance(retriever, BaseRetriever):
                all_retrievers.append(retriever)
            else:
                try:
                    all_retrievers.append(Retrievers[str(retriever)].value())
                except KeyError:
                    logger.error(f"Unsupported retrieval method: {retriever}")

        return all_retrievers
