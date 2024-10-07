import os
import logging
from dotenv import load_dotenv
from pyaml_env import parse_config

from rag.models import RAGRequest, EmbeddingRequest
from rag.factory import RetrieverFactory
from rag.llm.factory import LLMFactory
from rag.llm.base import BaseLLM
from rag.retrievers import RetrieverClient

from sqlalchemy.orm import Session
from utils.embedding import get_embedding
from utils.streaming import StreamingHandlerFactory, StreamingHandler
from rag.messages import MessageBuilder

from config.base_config import rag_config

from langfuse.decorators import observe
from langfuse import Langfuse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", None)
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", None)
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", None)

langfuse = Langfuse(
  secret_key=LANGFUSE_SECRET_KEY,
  public_key=LANGFUSE_PUBLIC_KEY,
  host=LANGFUSE_HOST
)

class RAGProcessor:
    """
    Class implementing the RAG process
    """
    def __init__(self, max_tokens: int, temperature: float,
                 top_p: float, top_k: int):

        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.k_retrieve = top_k

    def get_session_data(self):
        # Path to the YAML configuration file
        CONFIG_PATH = os.path.join('config', 'config.yaml')

        # Load the YAML configuration file
        config = parse_config(CONFIG_PATH)

        return config

    @observe()
    async def retrieve(self, db: Session, request: RAGRequest, language: str = None, tag: str = None, k: int = 0, retriever_client: RetrieverClient = None):
        """
        Retrieve context documents related to the user input question.
        """
        rows = await retriever_client.get_documents(db, request.query, language=language, tag=tag, k=k)

        return rows if len(rows) > 0 else [{"text": "", "url": ""}]

    @observe()
    async def process(self, db: Session, request: RAGRequest, language: str = None, tag: str = None, streaming_handler: StreamingHandler = None, llm_client: BaseLLM = None, retriever_client: RetrieverClient = None, message_builder: MessageBuilder = None):
        """
        Process a RAGRequest to retrieve relevant documents and generate a response.

        This method retrieves relevant documents from the database, constructs a context from the documents, and then uses an LLM client to generate a response based on the request query and the context.
        """
        documents = await self.retrieve(db, request, language=language, tag=tag, k=self.k_retrieve, retriever_client=retriever_client)
        context_docs = "\n\nDOC: ".join([doc["text"] for doc in documents])
        source_url = documents[0]["url"]  # TO DO: display multiple sources in frontend

        # TO DO: Get chat history
        messages = message_builder.build_chat_prompt(context_docs=context_docs, query=request.query)

        event_stream = llm_client.call(messages)

        async for chunk in streaming_handler.generate_stream(event_stream, source_url):
            yield chunk

    async def process_request(self, db: Session, request: RAGRequest, language: str = None, tag: str = None):

        session_data = self.get_session_data()
        session_language = "de" #if language is None else language
        llm_model = session_data["rag"]["llm"]["model"]
        stream = session_data["rag"]["llm"]["stream"]
        retrieval_method = session_data["rag"]["retrieval"]["retrieval_method"]

        # pass session_data.get("llm_model") to get_llm_client
        llm_client = LLMFactory.get_llm_client(llm_model=llm_model, stream=stream, temperature=self.temperature, top_p=self.top_p, max_tokens=self.max_tokens)
        message_builder = MessageBuilder(session_language=session_language, llm_model=llm_model)
        retriever_client = RetrieverFactory.get_retriever_client(retrieval_method=retrieval_method, llm_client=llm_client)
        streaming_handler = StreamingHandlerFactory.get_streaming_strategy(llm_model=llm_model)

        return self.process(db=db, request=request, language=language, tag=tag, streaming_handler=streaming_handler, llm_client=llm_client, retriever_client=retriever_client, message_builder=message_builder)

    async def embed(self, text_input: EmbeddingRequest):
        """
        Get the embedding of an embedding request.
        """
        embedding = await get_embedding(text_input.text)
        return {"data": embedding}

processor = RAGProcessor(max_tokens=rag_config["llm"]["max_output_tokens"],
                         temperature=rag_config["llm"]["temperature"],
                         top_p=rag_config["llm"]["top_p"],
                         top_k=rag_config["retrieval"]["top_k"])
