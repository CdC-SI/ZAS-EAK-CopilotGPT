from typing import List, Union

# Import env vars
from config.base_config import rag_config
from rag.embedding.factory import EmbeddingFactory

import openai

import logging
logger = logging.getLogger(__name__)

embedding_client = EmbeddingFactory.get_embedding_client(model_name=rag_config["embedding"]["model"])

# Function to get embeddings for a text
def get_embedding(texts: Union[List[str], str]) -> Union[List[float], List[List[float]]]:

    try:
        embedding = embedding_client.embed(
            texts=texts,
        )
        return embedding
    except openai.BadRequestError as e:
        logger.error(e.message)
        logger.error(f"Failed to get embeddings for text of length: {len(text)}")
        return None
