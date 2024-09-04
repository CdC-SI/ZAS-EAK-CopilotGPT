from typing import List, Union

# Import env vars
from config.config import RAGConfig
from config.clients_config import Clients

import openai

import logging
logger = logging.getLogger(__name__)

embedding_client = Clients.EMBEDDING.value


# Function to get embeddings for a text
def get_embedding(text: Union[List[str], str]):
    try:
        response = embedding_client.embeddings.create(
            input=text,
            model=RAGConfig.Embedding.value.name,
        )
        return response.data[0].embedding
    except openai.BadRequestError as e:
        logger.error(e.message)
        logger.error(f"Failed to get embeddings for text of length: {len(text)}")
        return None
