"""**Embeddings** interface."""
from abc import ABC, abstractmethod
from typing import List

class Embedding(ABC):
    """
    Abstract base class for embedding models.

    Attributes
    ----------
    tokenizer : Tokenizer
        The tokenizer instance.

    Methods
    -------
    truncate_text(text: str) -> str:
        Truncates a text to fit the embedding model size.
    embed_documents(texts: List[str]) -> List[List[float]]:
        Abstract method to embed a list of documents.
    embed_query(text: str) -> List[float]:
        Abstract method to embed a single query text.
    aembed_documents(texts: List[str]) -> List[List[float]]:
        Abstract method to asynchronously embed a list of documents.
    aembed_query(text: str) -> List[float]:
        Abstract method to asynchronously embed a single query text.
    """

    def __init__(self, tokenizer):
        """
        Initializes the Embedding instance.

        Parameters
        ----------
        tokenizer : Tokenizer
            The tokenizer instance.
        """
        self.tokenizer = tokenizer

    def truncate_text(self, text: str) -> str:
        """
        Truncates a text to fit the embedding model size.

        Parameters
        ----------
        text : str
            The text to truncate.

        Returns
        -------
        str
            The truncated text.
        """
        n_tokens = len(self.tokenizer.encode(text))
        if n_tokens > self.tokenizer.max_input_tokens:
            text = text[:self.tokenizer.max_input_tokens + 1]
        return text

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Abstract method to embed a list of documents.

        Parameters
        ----------
        texts : list of str
            The list of texts to embed.

        Returns
        -------
        list of list of float
            The embeddings for the texts.
        """
        return [self.truncate_text(text) for text in texts]

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Abstract method to embed a single query text.

        Parameters
        ----------
        text : str
            The text to embed.

        Returns
        -------
        list of float
            The embedding for the text.
        """

    @abstractmethod
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Abstract method to asynchronously embed a list of documents.

        Parameters
        ----------
        texts : list of str
            The list of texts to embed.

        Returns
        -------
        list of list of float
            The embeddings for the texts.
        """
        return [self.truncate_text(text) for text in texts]

    @abstractmethod
    async def aembed_query(self, text: str) -> List[float]:
        """
        Abstract method to asynchronously embed a single query text.

        Parameters
        ----------
        text : str
            The text to embed.

        Returns
        -------
        list of float
            The embedding for the text.
        """