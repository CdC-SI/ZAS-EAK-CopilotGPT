import csv

from config.base_config import rag_config
from rag.base import BaseRetriever, BaseRouter
from rag.retrievers import RetrieverClient, TopKRetriever, QueryRewritingRetriever, ContextualCompressionRetriever, RAGFusionRetriever, BM25Retriever, Reranker
from rag.llm.base import BaseLLM

from semantic_router import Route
from semantic_router.layer import RouteLayer
from semantic_router.encoders import OpenAIEncoder

class RetrieverFactory:
    """
    A factory class for creating a RetrieverClient based on the specified retrieval methods.

    This factory method allows for the creation of a composite retriever client that can use multiple
    retrieval strategies in sequence or in parallel, depending on the specified methods.

    Methods
    -------
    get_retriever_client(retrieval_method: str) -> BaseRetriever
        Creates a RetrieverClient instance configured with the specified retrieval methods.

    """
    @staticmethod
    def get_retriever_client(retrieval_method: str, llm_client: BaseLLM = None) -> BaseRetriever:
        """
        Create a RetrieverClient based on the given retrieval method(s).

        Parameters
        ----------
        retrieval_method : str
            A string or a list of strings specifying the retrieval methods to use. Supported methods are:
            - "top_k"
            - "query_rewriting"
            - "contextual_compression"
            - "RAGFusion"
            - "bm25"
            - "reranking"
        llm_client : BaseLLM, optional

        Returns
        -------
        BaseRetriever
            A RetrieverClient instance configured with the specified retrieval methods.

        Raises
        ------
        ValueError
            If an unsupported retrieval method is provided.
        """
        retrievers = []
        reranker = None

        for method in retrieval_method:
            match method:
                case "top_k_retriever":
                    retrievers.append(TopKRetriever(top_k=rag_config["retrieval"]["top_k_retriever_params"]["top_k"],))
                case "query_rewriting_retriever":
                    retrievers.append(QueryRewritingRetriever(n_alt_queries=rag_config["retrieval"]["query_rewriting_retriever_params"]["n_alt_queries"],
                                                              top_k=rag_config["retrieval"]["query_rewriting_retriever_params"]["top_k"],
                                                              llm_client=llm_client))
                case "contextual_compression_retriever":
                    retrievers.append(ContextualCompressionRetriever(top_k=rag_config["retrieval"]["contextual_compression_retriever_params"]["top_k"],
                                      llm_client=llm_client))
                case "bm25_retriever":
                    retrievers.append(BM25Retriever(k=rag_config["retrieval"]["bm25_retriever_params"]["k"],
                                                    b=rag_config["retrieval"]["bm25_retriever_params"]["k"],
                                                    top_k=rag_config["retrieval"]["bm25_retriever_params"]["top_k"],))
                case "rag_fusion_retriever":
                    retrievers.append(RAGFusionRetriever(n_alt_queries=rag_config["retrieval"]["rag_fusion_retriever_params"]["n_alt_queries"],
                                                         rrf_k=rag_config["retrieval"]["rag_fusion_retriever_params"]["rrf_k"],
                                                         top_k=rag_config["retrieval"]["rag_fusion_retriever_params"]["top_k"],
                                                         llm_client=llm_client))
                case "reranking":
                    reranker = Reranker(model=rag_config["retrieval"]["reranking_params"]["model"],
                                        top_k=rag_config["retrieval"]["reranking_params"]["top_k"],)
                case _:
                    raise ValueError(f"Unsupported retrieval method: {method}. Please refer to the documentation for supported methods (https://cdc-si.github.io/ZAS-EAK-CopilotGPT/).")

        client = RetrieverClient(retrievers=retrievers, reranker=reranker)
        return client

fz_utterances_q = []
with open('./indexing/data/fz_utterances_q.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        fz_utterances_q.append(row[0])

allgemeines_utterances_q = []
with open('./indexing/data/allgemeines_utterances_q.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        allgemeines_utterances_q.append(row[0])

familienzulage = Route(
    name="familienzulage",
    utterances=fz_utterances_q,
)

allgemeines = Route(
    name="allgemeines",
    utterances=allgemeines_utterances_q,
)

routes = [familienzulage, allgemeines]

class RouterFactory:
    """
    A factory class for creating a RouterClient based on the specified router model.

    Methods
    -------
    get_router_client(router: str) -> BaseRouter
        Creates a RouterClient instance configured with the specified embedding model.

    """
    @staticmethod
    def get_router_client(router: str) -> BaseRouter:
        """
        Create a RouterClient based on the given retrieval method(s).

        Parameters
        ----------
        router : str
            A string specifying the routing model to use. Supported models are:
            - "openai"

        Returns
        -------
        BaseRouter
            A RouterClient instance configured with the specified embedding model.

        Raises
        ------
        ValueError
            If an unsupported retrieval method is provided.
        """
        match router:
            case "openai":
                return RouteLayer(encoder=OpenAIEncoder(), routes=routes)
            case _:
                raise ValueError(f"Unsupported router model: {router}. Please refer to the documentation for supported models (https://cdc-si.github.io/ZAS-EAK-CopilotGPT/).")

