import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pyaml_env import parse_config

from rag.models import RAGRequest, EmbeddingRequest
from rag.factory import RetrieverFactory
from rag.llm.factory import LLMFactory
from rag.llm.base import BaseLLM
from rag.retrievers import RetrieverClient
from chat.memory import ConversationalMemory

from sqlalchemy.orm import Session
from utils.embedding import get_embedding
from utils.streaming import StreamingHandlerFactory, StreamingHandler
from rag.messages import MessageBuilder

from config.base_config import chat_config
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

class RAGService:
    """
    Class implementing the RAG process
    """
    def __init__(self, stream: bool, max_tokens: int, temperature: float,
                 top_p: float, top_k: int, memory_type: str, k_memory: int):

        self.stream = stream
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.k_retrieve = top_k
        self.chat_memory = ConversationalMemory(
            memory_type=memory_type,
            k_memory=k_memory
        )

    def get_session_data(self):
        # Path to the YAML configuration file
        CONFIG_PATH = os.path.join('config', 'config.yaml')

        # Load the YAML configuration file
        config = parse_config(CONFIG_PATH)

        return config

    async def embed(self, text_input: EmbeddingRequest):
        """
        Get the embedding of an embedding request.
        """
        embedding = await get_embedding(text_input.text)
        return {"data": embedding}

    @observe()
    async def retrieve(self, db: Session, request: RAGRequest, language: str = None, tag: str = None, k: int = 0, retriever_client: RetrieverClient = None):
        """
        Retrieve context documents related to the user input question.
        """
        rows = await retriever_client.get_documents(db, request.query, language=language, tag=tag, k=k)

        return rows if len(rows) > 0 else [{"text": "", "url": ""}]

    @observe()
    async def process(self, db: Session, llm_client: BaseLLM, streaming_handler: StreamingHandler, retriever_client: RetrieverClient, message_builder: MessageBuilder, request: RAGRequest, language: Optional[str] = None, tag: Optional[str] = None, user_uuid: str = None, conversation_uuid: str = None, conversational_memory: List[Dict] = None):
        """
        Process a RAGRequest to retrieve relevant documents and generate a response.

        This method retrieves relevant documents from the database, constructs a context from the documents, and then uses an LLM client to generate a response based on the request query and the context.
        """
        documents = await self.retrieve(db, request, language=language, tag=tag, k=self.k_retrieve, retriever_client=retriever_client)
        context_docs = "\n\nDOC: ".join([doc["text"] for doc in documents])
        source_url = documents[0]["url"]  # TO DO: display multiple sources in frontend

        messages = message_builder.build_chat_prompt(context_docs=context_docs, query=request.query, conversational_memory=conversational_memory)

        event_stream = llm_client.call(messages)

        assistant_response = []
        async for token in streaming_handler.generate_stream(event_stream, source_url):
            assistant_response.append(token.decode("utf-8"))
            yield token

        # Index query in chat history
        self.chat_memory.memory_instance.add_message_to_memory(db, user_uuid, conversation_uuid, "user", request.query)

        # Index chat response in chat history
        retrieved_doc_ids = [doc["id"] for doc in documents]
        self.chat_memory.memory_instance.add_message_to_memory(db, user_uuid, conversation_uuid, "assistant", "".join(assistant_response), retrieved_doc_ids=retrieved_doc_ids)

        # Save chat title
        if not self.chat_memory.memory_instance.conversation_uuid_exists(db, conversation_uuid):
            create_title_message = message_builder.build_chat_title_prompt(query=request.query, assistant_response=assistant_response)
            chat_title = await llm_client.agenerate(create_title_message)
            self.chat_memory.memory_instance.index_chat_title(db, user_uuid, conversation_uuid, chat_title.choices[0].message.content)

    async def process_request(self, db: Session, request: RAGRequest, language: Optional[str] = None, tag: Optional[str] = None, source: Optional[str] = None, llm_model: Optional[str] = rag_config["llm"]["model"], retrieval_method: Optional[List[str]] = rag_config["retrieval"]["retrieval_method"], k_memory: Optional[int] = chat_config["memory"]["k_memory"], user_uuid: Optional[str] = None, conversation_uuid: Optional[str] = None):

        conversational_memory = self.chat_memory.memory_instance.fetch_from_memory(user_uuid, conversation_uuid)
        conversational_memory = "\n".join([f"{role}: {message}" for msg in conversational_memory for role, message in msg.items()])

        llm_client = LLMFactory.get_llm_client(llm_model=llm_model, stream=self.stream, temperature=self.temperature, top_p=self.top_p, max_tokens=self.max_tokens)
        message_builder = MessageBuilder(language=language, llm_model=llm_model)
        retriever_client = RetrieverFactory.get_retriever_client(retrieval_method=retrieval_method, llm_client=llm_client, message_builder=message_builder)
        streaming_handler = StreamingHandlerFactory.get_streaming_strategy(llm_model=llm_model)

        return self.process(db=db, llm_client=llm_client, streaming_handler=streaming_handler, retriever_client=retriever_client, message_builder=message_builder, request=request, language=language, tag=tag, user_uuid=user_uuid, conversation_uuid=conversation_uuid, conversational_memory=conversational_memory)

rag_service = RAGService(
    stream=rag_config["llm"]["stream"],
    max_tokens=rag_config["llm"]["max_output_tokens"],
    temperature=rag_config["llm"]["temperature"],
    top_p=rag_config["llm"]["top_p"],
    top_k=rag_config["retrieval"]["top_k"],
    memory_type=chat_config["memory"]["memory_type"],
    k_memory=chat_config["memory"]["k_memory"]
    )
