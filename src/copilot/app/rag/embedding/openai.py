import logging
from typing import List, Union
from rag.embedding.base import BaseEmbedding
from rag.tokenizer.factory import TokenizerFactory

# Import env vars
from config.clients_config import clientEmbed
from config.llm_config import DEFAULT_OPENAI_EMBEDDING_MODEL

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OpenAIEmbedding(BaseEmbedding):
    """
    Class for embedding text documents using OpenAI's models.

    Attributes
    ----------
    model_name : str
        The name of the OpenAI model to use for embedding.
    client : openai.OpenAI
        The OpenAI client.
    tokenizer : Tokenizer
        The tokenizer instance.

    Methods
    -------
    embed(texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        Embeds a single text query or a list of text documents using the OpenAI API.
    """
    def __init__(self, model_name: str = DEFAULT_OPENAI_EMBEDDING_MODEL):
        """
        Initializes the OpenAIEmbeddings instance.

        Parameters
        ----------
        model_name : str, optional
            The name of the OpenAI model to use for embedding. If not provided,
            the default model is used.
        """
        self.model_name = model_name
        self.client = clientEmbed
        self.tokenizer = TokenizerFactory.get_tokenizer_client(self.model_name)
        super().__init__(self.tokenizer)

    def embed(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Embeds a single text query or a list of text documents using the OpenAI API.

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
            If the API call fails.
        """
        if isinstance(texts, str):
            texts = [texts]
            single_query = True
        else:
            single_query = False

        texts = super()._embed_documents(texts)
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts,
            )
            embedding = response.data
            return embedding[0].embedding if single_query else embedding
        except Exception as e:
            raise e
