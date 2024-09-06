from typing import List, Union

# Import env vars
from config.config import IndexingConfig
from config.clients_config import Clients

import openai

from utils.logging import get_logger
logger = get_logger(__name__)

CLIENT = Clients.EMBEDDING.value
MODEL = IndexingConfig.Embedding.value.name


class Embedder:

    @staticmethod
    def embed(text: Union[List[str], str]):
        """
        Get embeddings for a list of texts or a single text.

        Returns
        -------
        list of list[float] or list[float]
            List of embeddings for each text in the input list or a single embedding for a single text.
        """
        try:
            response = CLIENT.embeddings.create(
                input=text,
                model=MODEL,
            )
            return response.data[0].embedding
        except openai.BadRequestError as e:
            logger.error(e.message)
            logger.error(f"Failed to get embeddings for text of length: {len(text)}")
            return None
