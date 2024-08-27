from rag.embedding.base import BaseEmbedding
from rag.embedding import *
from config.llm_config import SUPPORTED_OPENAI_EMBEDDING_MODELS, SUPPORTED_ST_EMBEDDING_MODELS

class EmbeddingFactory:
    """
    Factory class for creating embedding clients.

    This class provides a static method to create instances of embedding clients based on a string identifier.

    Methods
    -------
    get_embedding_client(embedding_model: str) -> Embedding
        Factory method to instantiate embedding clients based on a string identifier.
    """

    @staticmethod
    def get_embedding_client(model_name: str) -> BaseEmbedding:
        """
        Factory method to instantiate embedding clients based on a string identifier.

        Parameters
        ----------
        embedding_model : str
            The name of the embedding model. Currently supported models are "text-embedding-ada-002" and
            "sentence-transformers/distiluse-base-multilingual-cased-v1".

        Returns
        -------
        Embedding
            An instance of the appropriate embedding client.

        Raises
        ------
        ValueError
            If the `embedding_model` is not supported.
        """
        if model_name in SUPPORTED_OPENAI_EMBEDDING_MODELS:
            return OpenAIEmbedding(model_name=model_name)
        elif model_name in SUPPORTED_ST_EMBEDDING_MODELS:
            return SentenceTransformersEmbedding(model_name=model_name)
        else:
            raise ValueError(f"Unsupported embedding model type: {model_name}")