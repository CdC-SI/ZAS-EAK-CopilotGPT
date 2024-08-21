from typing import List, Union

# Import env vars
from config.base_config import rag_config
from config.clients_config import clientEmbed

import openai

supported_models = ["text-embedding-ada-002", "text-embedding-3-large", "text-embedding-3-small"]

logger = logging.getLogger(__name__)


# Function to get embeddings for a text
def get_embedding(text: Union[List[str], str]):
    try:
        response = clientEmbed.embeddings.create(
            input=text,
            model=rag_config["embedding"]["model"],
        )
        return response.data[0].embedding
    except openai.BadRequestError as e:
        logger.error(e.message)
        logger.error(f"Failed to get embeddings for text of length: {len(text)}")
        return None
