"""**Embeddings** interface."""
from abc import ABC
from typing import List, Union

class BaseEmbedding(ABC):
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
        tokenized_text = self.tokenizer.encode(text)
        n_tokens = len(tokenized_text)
        if n_tokens > self.tokenizer.max_input_tokens:
            tokenized_text = tokenized_text[:self.tokenizer.max_input_tokens - 1]
            text = self.tokenizer.decode(tokenized_text)
        return text

    def _embed_documents(self, texts: List[str]) -> List[List[float]]:
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

    def _embed_query(self, text: str) -> List[float]:
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
        return self.truncate_text(text)

    def embed(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Abstract method to embed a single text query or a list of text documents.

        Parameters
        ----------
        texts : str or list of str
            The text or list of texts to embed.

        Returns
        -------
        list of float or list of list of float
            The embedding for the text or list of embeddings, one for each text.
        """
        if isinstance(texts, str):
            return self._embed_query(texts)
        elif isinstance(texts, list):
            return self._embed_documents(texts)
