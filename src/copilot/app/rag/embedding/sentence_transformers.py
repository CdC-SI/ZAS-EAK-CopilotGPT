import logging
from typing import List, Union
from rag.embedding.base import BaseEmbedding
from rag.tokenizer.factory import TokenizerFactory

from sentence_transformers import SentenceTransformer

# Import env vars
from config.llm_config import DEFAULT_ST_EMBEDDING_MODEL

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SentenceTransformersEmbedding(BaseEmbedding):
    """
    Class for embedding text documents using SentenceTransformers models.

    Attributes
    ----------
    model_name : str
        The name of the ST model to use for embedding.
    client : SentenceTransformer
        The ST client.
    tokenizer : Tokenizer
        The tokenizer instance.

    Methods
    -------
    embed(texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        Embeds a single text query or a list of text documents using the embedding model.
    """
    def __init__(self, model_name: str = DEFAULT_ST_EMBEDDING_MODEL):
        """
        Initializes the OpenAIEmbeddings instance.

        Parameters
        ----------
        model_name : str, optional
            The name of the OpenAI model to use for embedding. If not provided,
            the default model is used.
        """
        self.model_name = model_name
        self.client = SentenceTransformer(self.model_name)
        self.tokenizer = TokenizerFactory.get_tokenizer_client(self.model_name)
        super().__init__(self.tokenizer)

    def embed(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Embeds a single text query or a list of text documents using the ST embedding model.

        Parameters
        ----------
        texts : Union[str, list of str]
            The text or list of texts to embed.

        Returns
        -------
        Union[list of float, list of list of float]
            Embedding for the text or list of embeddings, one for each text.

        Raises
        ------
        Exception
            If the embedding call fails.
        """
        if isinstance(texts, str):
            texts = [texts]

        texts = super()._embed_documents(texts)
        try:
            embedding = self.client.encode(texts)
            return embedding
        except Exception as e:
            raise e
