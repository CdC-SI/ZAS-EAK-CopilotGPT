from config.base_config import rag_config
from rag.retrievers import (
    BaseRetriever,
    RetrieverClient,
    TopKRetriever,
    QueryRewritingRetriever,
    ContextualCompressionRetriever,
    RAGFusionRetriever,
    BM25Retriever,
    Reranker,
)
from config.clients_config import clientRerank
from llm.base import BaseLLM
from chat.messages import MessageBuilder


class RetrieverFactory:
    """
    A factory class for creating a RetrieverClient based on the specified retrieval methods.

    This factory method allows for the creation of a composite retriever client that can use multiple
    retrieval strategies in sequence or asynchronously, depending on the specified methods.
    """

    @staticmethod
    def get_retriever_client(
        retrieval_method: str = rag_config["retrieval"]["retrieval_method"],
        llm_client: BaseLLM = None,
        message_builder: MessageBuilder = None,
    ) -> BaseRetriever:
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
                    retrievers.append(
                        TopKRetriever(
                            top_k=rag_config["retrieval"][
                                "top_k_retriever_params"
                            ]["top_k"],
                        )
                    )
                case "query_rewriting_retriever":
                    retrievers.append(
                        QueryRewritingRetriever(
                            n_alt_queries=rag_config["retrieval"][
                                "query_rewriting_retriever_params"
                            ]["n_alt_queries"],
                            top_k=rag_config["retrieval"][
                                "query_rewriting_retriever_params"
                            ]["top_k"],
                            llm_client=llm_client,
                            message_builder=message_builder,
                        )
                    )
                case "contextual_compression_retriever":
                    retrievers.append(
                        ContextualCompressionRetriever(
                            top_k=rag_config["retrieval"][
                                "contextual_compression_retriever_params"
                            ]["top_k"],
                            llm_client=llm_client,
                            message_builder=message_builder,
                        )
                    )
                case "bm25_retriever":
                    retrievers.append(
                        BM25Retriever(
                            k=rag_config["retrieval"]["bm25_retriever_params"][
                                "k"
                            ],
                            b=rag_config["retrieval"]["bm25_retriever_params"][
                                "b"
                            ],
                            top_k=rag_config["retrieval"][
                                "bm25_retriever_params"
                            ]["top_k"],
                        )
                    )
                case "rag_fusion_retriever":
                    retrievers.append(
                        RAGFusionRetriever(
                            n_alt_queries=rag_config["retrieval"][
                                "rag_fusion_retriever_params"
                            ]["n_alt_queries"],
                            rrf_k=rag_config["retrieval"][
                                "rag_fusion_retriever_params"
                            ]["rrf_k"],
                            top_k=rag_config["retrieval"][
                                "rag_fusion_retriever_params"
                            ]["top_k"],
                            llm_client=llm_client,
                            message_builder=message_builder,
                        )
                    )
                case "reranking":
                    reranker = (
                        Reranker(
                            model=rag_config["retrieval"]["reranking_params"][
                                "model"
                            ],
                        )
                        if clientRerank is not None
                        else None
                    )
                case _:
                    raise ValueError(
                        f"Unsupported retrieval method: {method}. Please refer to the documentation for supported methods (https://cdc-si.github.io/ZAS-EAK-CopilotGPT/)."
                    )

        client = RetrieverClient(retrievers=retrievers, reranker=reranker)
        return client
