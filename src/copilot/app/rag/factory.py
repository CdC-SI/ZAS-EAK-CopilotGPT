from rag.base import BaseRetriever
from rag.retrievers import TopKRetriever

class RetrieverFactory:
    @staticmethod
    def get_retriever_client(retrieval_method: str) -> BaseRetriever:
        """
        Factory method to instantiate retriever clients based on a string identifier.

        Parameters
        ----------
        retriever : str
            The name of the retriever. Currently supported models are "simple", "query_rewriting", "contextual_compression", "bm25" and "reranking".

        Returns
        -------
        BaseRetriever
            An instance of the appropriate retriever client.

        Raises
        ------
        ValueError
            If the `retriever` is not supported.
        """
        retrieval_method = retrieval_method[0]

        # switch/case statements
        #if retriever_name not in SUPPORTED_RETRIEVAL_METHODS:
        if retrieval_method not in ["top_k", "query_rewriting", "contextual_compression", "bm25", "reranking"]:
            raise ValueError(f"Unsupported retrieval method: {retrieval_method}")
        elif retrieval_method == "top_k":
            return TopKRetriever()
        # elif retriever_name == "query_rewriting":
        #     return OpenAILLM(model_name=llm_model)
        # elif retriever_name == "contextual_compression":
        #     return OpenAILLM(model_name=llm_model)
        # elif retriever_name == "bm25":
        #     return OpenAILLM(model_name=llm_model)
        # elif retriever_name == "reranking":
        #     return OpenAILLM(model_name=llm_model)
