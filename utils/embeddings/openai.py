from typing import List
from utils.embeddings.embeddings import Embeddings

# Import env vars
from config.base_config import rag_config
from config.openai_config import openai

DEFAULT_OPENAI_MODEL = "text-embedding-ada-002"
SUPPORTED_MODELS = ["text-embedding-ada-002",
                    "sentence-transformers/distiluse-base-multilingual-cased-v1"]

# DANS INIT + logging à la place de Raise
if rag_config["embedding"]["model"] not in SUPPORTED_MODELS:
    raise ValueError(
        f"Model '{rag_config['embedding']['model']}' is not supported")


class OpenAIEmbeddings(Embeddings):
    """
    OpenAI API embedding model.

    To use, you should have the ``openai`` python package installed.

    Attributes
    ----------
    model_name : str
        The model name to be used for embeddings, defaults to DEFAULT_OPENAI_MODEL if not provided in rag_config.

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
    >>> openai_embeddings.embed_documents(["Guten", "Morgen"])
    >>> openai_embeddings.embed_query("Guten Morgen")
    """
    def __init__(self, model_name: str = DEFAULT_OPENAI_MODEL):
        self.model_name = model_name if model_name else 
        self.client = openai.OpenAI()

    #model_name = rag_config["embedding"]["model"] if rag_config["embedding"]["model"] is not None else DEFAULT_OPENAI_MODEL
    #self.client = openai.OpenAI()

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