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
    """
    OpenAI API embedding model.

    To use, you should have the ``openai`` python package installed.

    Attributes
    ----------
    model : str
        The model to be used for embeddings, defaults to DEFAULT_OPENAI_MODEL if not provided in rag_config.

    Methods
    -------
    embed_documents(texts)
        Makes a call to the OpenAI embedding API to embed a list of text documents.
    embed_query(text)
        Makes a call to the OpenAI embedding API to embed a single text query.

    Example
    -------
    >>> from utils.embeddings import OpenAIEmbeddings
    >>> model_name = "text-embedding-ada-002"
    >>> openai_embeddings = OpenAIEmbeddings(
    >>>     model_name=model_name,
    >>>     input=text
    >>> )
    """
    model = rag_config["embedding"]["model"] if rag_config["embedding"]["model"] is not None else DEFAULT_OPENAI_MODEL

    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        """
        Makes a call to the OpenAI embedding API to embed a list of text documents.

        Parameters
        ----------
        texts : list of str
            The list of texts to embed.

        Returns
        -------
        list of list of float
            List of embeddings, one for each text.

        Raises
        ------
        Exception
            If the API call fails.
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
        """
        Makes a call to the OpenAI embedding API to embed a single text query.

        Parameters
        ----------
        text : str
            The text to embed.

        Returns
        -------
        list of float
            Embedding for the text.
        """
        return cls.embed_documents([text])[0]
