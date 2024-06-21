import logging

from typing import List
from utils.embeddings.embeddings import Embedding

from sentence_transformers import SentenceTransformer

# Import env vars
from config.base_config import rag_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_ST_MODEL = "sentence-transformers/distiluse-base-multilingual-cased-v1"
SUPPORTED_ST_MODELS = ["sentence-transformers/distiluse-base-multilingual-cased-v1"]


class SentenceTransformersEmbeddings(Embedding):
    """
    SentenceTransformers embedding model.

    To use, you should have the ``sentence-transformers`` python package installed.

    Attributes
    ----------
    model_name : str
        The model name to be used for embeddings, defaults to DEFAULT_ST_MODEL if not provided in rag_config.

    Methods
    -------
    embed_documents(texts)
        Makes a call to the SentenceTransformers embedding model (running locally) to embed a list of text documents.
    embed_query(text)
        Makes a call to the SentenceTransformers embedding model (running locally) to embed a single text query.

    Example
    -------
    >>> from utils.embeddings import SentenceTransformersEmbeddings
    >>> model_name = "sentence-transformers/distiluse-base-multilingual-cased-v1"
    >>> st_embeddings = SentenceTransformersEmbeddings(
    >>>     model_name=model_name,
    >>>     input=text
    >>> )
    >>> st_embeddings.embed_documents(["Guten", "Morgen"])
    >>> st_embeddings.embed_query("Guten Morgen")
    """
    def __init__(self, model_name: str = DEFAULT_ST_MODEL):
        self.model_name = model_name if model_name is not None and model_name in SUPPORTED_ST_MODELS else DEFAULT_ST_MODEL
        self.client = SentenceTransformer(self.model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Makes a call to the SentenceTransformers embedding model (running locally) to embed a list of text documents.

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
            If the embedding call fails.
        """
        try:
            response = self.client.encode(texts).tolist()
            return response
        except Exception as e:
            raise e

    def embed_query(self, text: str) -> List[float]:
        """
        Makes a call to the SentenceTransformers embedding model (running locally) to embed a single text query.

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
