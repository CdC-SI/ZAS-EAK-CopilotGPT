import os
import logging
from dotenv import load_dotenv
from pyaml_env import parse_config

from typing import List, Dict, Any

from rag.models import RAGRequest, EmbeddingRequest
from rag.factory import RetrieverFactory
from rag.llm.factory import LLMFactory
from rag.llm.base import BaseLLM
from rag.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE
from rag.retrievers import RetrieverClient

from sqlalchemy.orm import Session
from utils.embedding import get_embedding
from utils.streaming import StreamingHandlerFactory, StreamingHandler

from config.base_config import rag_config
from config.llm_config import SUPPORTED_OPENAI_LLM_MODELS, SUPPORTED_AZUREOPENAI_LLM_MODELS, SUPPORTED_ANTHROPIC_LLM_MODELS, SUPPORTED_GROQ_LLM_MODELS

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

    Parameters
    ----------
    llm : BaseLLM
    max_token : int
    temperature : float
    top_p : float
    retriever :
    top_k : int
    """
    # def __init__(self, llm: BaseLLM, max_token: int, temperature: float,
    #              top_p: float, retriever, top_k: int):

    #     self.llm_client = llm
    #     self.max_tokens = max_token
    #     self.temperature = temperature
    #     self.top_p = top_p
    #     self.retriever_client = retriever
    #     self.k_retrieve = top_k

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
    def create_rag_message(self, context_docs: List[Any], query: str) -> List[Dict]:
        """
        Format the RAG message to send to the OpenAI API.

        Parameters
        ----------
        context_docs : str
            Context matching the query according to the retrieval process
        query : str
            User input question

        Returns
        -------
        list of dict
            Contains the message in the correct format to send to the OpenAI API

        """
        openai_rag_system_prompt = OPENAI_RAG_SYSTEM_PROMPT_DE.format(context_docs=context_docs, query=query)
        if rag_config["llm"]["model"] in SUPPORTED_OPENAI_LLM_MODELS + SUPPORTED_AZUREOPENAI_LLM_MODELS + SUPPORTED_GROQ_LLM_MODELS:
            return [{"role": "system", "content": openai_rag_system_prompt},]
        elif rag_config["llm"]["model"] in SUPPORTED_ANTHROPIC_LLM_MODELS:
            return [{"role": "user", "content": openai_rag_system_prompt},]

    @observe()
    async def retrieve(self, db: Session, request: RAGRequest, language: str = None, tag: str = None, k: int = 0, retriever_client: RetrieverClient = None):
        """
        Retrieve context documents related to the user input question.

        Parameters
        ----------
        db : Session
            Database session
        request : RAGRequest
            User input question
        language : str
            Question and context documents language
        tag : str
            Tag to filter the context documents
        k : int, default 0
            Number of context documents to return
        """
        #rows = self.retriever_client.get_documents(db, request.query, language=language, tag=tag, k=k)
        rows = await retriever_client.get_documents(db, request.query, language=language, tag=tag, k=k)

        return rows if len(rows) > 0 else [{"text": "", "url": ""}]

    @observe()
    async def process(self, db: Session, request: RAGRequest, language: str = None, tag: str = None, streaming_handler: StreamingHandler = None, llm_client: BaseLLM = None, retriever_client: RetrieverClient = None):
        """
        Process a RAGRequest to retrieve relevant documents and generate a response.

        This method retrieves relevant documents from the database, constructs a context from the documents, and then uses an LLM client to generate a response based on the request query and the context.

        Parameters
        ----------
        db : Session
            The database session to use for retrieving documents.
        request : RAGRequest
            The request to process.
        language : str, optional
            The language of the documents to retrieve. If not specified, documents in all languages are considered.
        tag : str, optional
            The tag to filter the documents to retrieve. If not specified, all documents are considered.

        Returns
        -------
        str
            The response generated by the LLM client.
        """
        documents = await self.retrieve(db, request, language=language, tag=tag, k=self.k_retrieve, retriever_client=retriever_client)
        #documents = retriever_client.get_documents(db, request.query, language=language, tag=tag, k=self.k_retrieve)
        context_docs = "\n\nDOC: ".join([doc["text"] for doc in documents])  # TO UPDATE
        source_url = documents[0]["url"]  # TO UPDATE

        messages = self.create_rag_message(context_docs, request.query)

        #stream = self.llm_client.call(messages)
        event_stream = llm_client.call(messages)

        #return await streaming_handler.generate_stream(event_stream, source_url)
        async for chunk in streaming_handler.generate_stream(event_stream, source_url):
            yield chunk


    async def process_request(self, db: Session, request: RAGRequest, language: str = None, tag: str = None):

        #provider = get_user_provider(session)
        session_data = self.get_session_data()
        llm_model = session_data["rag"]["llm"]["model"]
        stream = session_data["rag"]["llm"]["stream"]
        retrieval_method = session_data["rag"]["retrieval"]["retrieval_method"]

        llm_client = LLMFactory.get_llm_client(llm_model=llm_model, stream=stream, temperature=self.temperature, top_p=self.top_p, max_tokens=self.max_tokens)
        retriever_client = RetrieverFactory.get_retriever_client(retrieval_method=retrieval_method, llm_client=llm_client)
        streaming_handler = StreamingHandlerFactory.get_streaming_strategy(llm_model)

        return self.process(db=db, request=request, language=language, tag=tag, streaming_handler=streaming_handler, llm_client=llm_client, retriever_client=retriever_client)

    async def embed(self, text_input: EmbeddingRequest):
        """
        Get the embedding of an embedding request.

        Parameters
        ----------
        text_input : EmbeddingRequest

        Returns
        -------
        dict
            The requested text embedding
        """
        embedding = await get_embedding(text_input.text)
        return {"data": embedding}

#llm_client = LLMFactory.get_llm_client(llm_model=rag_config["llm"]["model"], stream=rag_config["llm"]["stream"])
#retriever_client = RetrieverFactory.get_retriever_client(retrieval_method=rag_config["retrieval"]["retrieval_method"], llm_client=llm_client)

# processor = RAGProcessor(llm=llm_client,
#                          max_token=rag_config["llm"]["max_output_tokens"],
#                          temperature=rag_config["llm"]["temperature"],
#                          top_p=rag_config["llm"]["top_p"],
#                          retriever=retriever_client,
#                          top_k=rag_config["retrieval"]["top_k"])

processor = RAGProcessor(max_tokens=rag_config["llm"]["max_output_tokens"],
                         temperature=rag_config["llm"]["temperature"],
                         top_p=rag_config["llm"]["top_p"],
                         top_k=rag_config["retrieval"]["top_k"])
