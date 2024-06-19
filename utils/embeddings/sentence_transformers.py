from typing import Coroutine, List
from utils.embeddings.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

# Import env vars
from config.base_config import rag_config

DEFAULT_ST_MODEL = "sentence-transformers/distiluse-base-multilingual-cased-v1"
SUPPORTED_MODELS = ["sentence-transformers/distiluse-base-multilingual-cased-v1"]

if rag_config["embedding"]["model"] not in SUPPORTED_MODELS:
    raise ValueError(f"Model '{rag_config['embedding']['model']}' is not supported")

class SentenceTransformersEmbeddings(Embeddings):
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
    def __init__(self):
        model_name = rag_config["embedding"]["model"] if rag_config["embedding"]["model"] is not None else DEFAULT_ST_MODEL
        self.model = SentenceTransformer(model_name)

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
            response = self.model.encode(texts).tolist()
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
