from typing import List
from utils.embeddings.embeddings import Embeddings

# Import env vars
from config.base_config import rag_config
from config.openai_config import openai

DEFAULT_OPENAI_MODEL = "text-embedding-ada-002"
SUPPORTED_MODELS = ["text-embedding-ada-002"]

if rag_config["embedding"]["model"] not in SUPPORTED_MODELS:
    raise ValueError(f"Model '{rag_config['embedding']['model']}' is not supported")

class OpenAIEmbeddings(Embeddings):
    """OpenAI API embedding model.

    To use, you should have the ``openai`` python package installed.

    Example:
        .. code-block:: python

            from utils.embeddings import OpenAIEmbeddings

            model_name = "text-embedding-ada-002"
            openai_embeddings = OpenAIEmbeddings(
                model_name=model_name,
                input=text
            )
    """
    model = rag_config["embedding"]["model"] if rag_config["embedding"]["model"] is not None else DEFAULT_OPENAI_MODEL

    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        """Make call to OpenAI embedding API to embed a list of text documents.

        Args:
            texts: The list of texts to embed.


        Returns:
            List of embeddings, one for each text.
        """
        try:
            response = openai.embeddings.create(
                model=cls.model,
                input=texts,
                )
            return response.data
        except Exception as e:
            raise e

    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        """Make call to OpenAI embedding API to embed a single text query.

        Args:
            text: The text to embed.

        Returns:
            Embedding for the text.
        """
        return cls.embed_documents([text])[0]
