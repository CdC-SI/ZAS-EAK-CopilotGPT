from components.embeddings.base import Embedding
from components.embeddings.implementations.openai import OpenAIEmbeddings
from components.embeddings.implementations.sentence_transformers import SentenceTransformersEmbeddings

class EmbeddingFactory:
    @staticmethod
    def get_embedding_client(embedding_model: str) -> Embedding:
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
        if embedding_model == "text-embedding-ada-002":
            return OpenAIEmbeddings()
        elif embedding_model == "sentence-transformers/distiluse-base-multilingual-cased-v1":
            return SentenceTransformersEmbeddings()
        else:
            raise ValueError(f"Unsupported embedding model type: {embedding_model}")