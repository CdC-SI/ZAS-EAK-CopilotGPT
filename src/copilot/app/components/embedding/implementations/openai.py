import logging

from typing import List
from components.embedding.base import Embedding

# Import env vars
from config.openai_config import openai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_OPENAI_MODEL = "text-embedding-ada-002"
SUPPORTED_OPENAI_MODELS = ["text-embedding-ada-002"]


class OpenAIEmbeddings(Embedding):
    """
    OpenAI API embedding model.

    To use, you should have the ``openai`` python package installed.

    Attributes
    ----------
    model_name : str
        The model name to be used for embeddings, defaults to DEFAULT_OPENAI_MODEL if not provided in config.yaml.

    Methods
    -------
    embed_documents(texts)
        Makes a call to the OpenAI embedding API to embed a list of text documents.
    embed_query(text)
        Makes a call to the OpenAI embedding API to embed a single text query.

    Example
    -------
    >>> from components.embeddings.implementations.openai import OpenAIEmbeddings
    >>> model_name = "text-embedding-ada-002"
    >>> openai_embeddings = OpenAIEmbeddings(
    >>>     model_name=model_name,
    >>>     input=text
    >>> )
    >>> openai_embeddings.embed_documents(["Guten", "Morgen"])
    >>> openai_embeddings.embed_query("Guten Morgen")
    """
    def __init__(self, model_name: str = DEFAULT_OPENAI_MODEL):
        self.model_name = model_name if model_name is not None and model_name in SUPPORTED_OPENAI_MODELS else DEFAULT_OPENAI_MODEL
        self.client = openai.OpenAI()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
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
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts,
            )
            return response.data
        except Exception as e:
            raise e

    def embed_query(self, text: str) -> List[float]:
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
        return self.embed_documents([text])[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("This method is not implemented yet.")

    async def aembed_query(self, text: str) -> List[float]:
        raise NotImplementedError("This method is not implemented yet.")