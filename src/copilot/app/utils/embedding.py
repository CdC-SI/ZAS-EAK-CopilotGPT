from typing import List, Union
import logging

import openai

# Import env vars
from config.base_config import rag_config
from config.llm_config import SUPPORTED_OPENAI_EMBEDDING_MODELS
from config.openai_config import EmbeddingClientAI

logger = logging.getLogger(__name__)

# Function to get embeddings for a text
def get_embedding(text: Union[List[str], str]):
    model = rag_config["embedding"]["model"]
    if model in SUPPORTED_OPENAI_EMBEDDING_MODELS:
        try:
            response = EmbeddingClientAI.embeddings.create(
                input=text,
                model=model,
            )
            return response.data[0].embedding
        except openai.BadRequestError as e:
            logger.error(e.message)
            logger.error(f"Failed to get embeddings for text of length: {len(text)}")
            return None
    else:
        raise NotImplementedError(f"Model '{model}' is not supported")
