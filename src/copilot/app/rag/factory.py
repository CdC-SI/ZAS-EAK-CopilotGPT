from config.base_config import rag_config
from rag.base import BaseRetriever
from rag.retrievers import RetrieverClient, TopKRetriever, QueryRewritingRetriever, ContextualCompressionRetriever, BM25Retriever, Reranker

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
    def get_retriever_client(retrieval_method: str) -> BaseRetriever:
        """
        Create a RetrieverClient based on the given retrieval method(s).

        Parameters
        ----------
        retrieval_method : str
            A string or a list of strings specifying the retrieval methods to use. Supported methods are:
            - "top_k"
            - "query_rewriting"
            - "contextual_compression"
            - "bm25"
            - "reranking"

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

        for method in retrieval_method:
            match method:
                case "top_k_retriever":
                    retrievers.append(TopKRetriever(top_k=rag_config["retrieval"]["top_k_retriever_params"]["top_k"]))
                case "query_rewriting_retriever":
                    retrievers.append(QueryRewritingRetriever())
                case "contextual_compression_retriever":
                    retrievers.append(ContextualCompressionRetriever())
                case "bm25_retriever":
                    retrievers.append(BM25Retriever(k=rag_config["retrieval"]["bm25_retriever_params"]["k"],
                                                    b=rag_config["retrieval"]["bm25_retriever_params"]["k"],
                                                    top_k=rag_config["retrieval"]["bm25_retriever_params"]["top_k"]))
                case "reranking":
                    retrievers.append(Reranker())
                case _:
                    raise ValueError(f"Unsupported retrieval method: {method}. Please see the documentation for supported methods (https://cdc-si.github.io/ZAS-EAK-CopilotGPT/).")

        client = RetrieverClient(retrievers=retrievers)
        return client
