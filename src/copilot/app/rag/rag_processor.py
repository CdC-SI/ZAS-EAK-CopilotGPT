from rag.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE
from rag.models import RAGRequest, EmbeddingRequest
from rag.factory import RetrieverFactory

from sqlalchemy.orm import Session
from database.service import document_service
from utils.embedding import get_embedding

from config.openai_config import clientAI
from config.base_config import rag_config

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RAGProcessor:
    """
    Class implementing the RAG process

    Parameters
    ----------
    model : str
        LLM Model used for generating chatbot answers
    max_token : int
    stream : bool
    temperature : float
    top_p : float
    retriever :
    top_k : int
    client
    """
    def __init__(self, model: str, max_token: int, stream: bool, temperature: float,
                 top_p: float, retrieval_method: str, top_k: int, client):
        self.model = model
        self.max_tokens = max_token
        self.stream = stream
        self.temperature = temperature
        self.top_p = top_p
        self.retriever_client = self.init_retriever_client(retrieval_method=retrieval_method)
        self.k_retrieve = top_k

        self.client = client

    def init_retriever_client(self, retrieval_method: str = "top_k"):
        """
        Initialize and return a retriever client based on `retrieval_method`.

        Returns
        -------
        object
            An instance of the appropriate retriever client based on `retrieval_method`.
        """
        return RetrieverFactory.get_retriever_client(retrieval_method=retrieval_method)

    def retrieve(self, db: Session, request: RAGRequest, language: str = None, k: int = 0):
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
        k : int, default 0
            Number of context documents to return
        """
        rows = self.retriever_client.get_documents(db, request.query, language=language, k=k)

        return rows if len(rows) > 0 else [{"text": "", "url": ""}]

    def process(self, db: Session, request: RAGRequest, language: str = None):
        """
        Execute the RAG process and query the LLM model.

        Parameters
        ----------
        db : Session
            Database session
        request : RAGRequest
            User input question
        language : str
            Question and context documents language

        Returns
        -------
        str
            LLM generated answer to the question
        """
        documents = self.retrieve(db, request, language=language, k=self.k_retrieve)
        context_docs = "\n\n".join([doc.text for doc in documents]) # TO UPDATE
        source_url = documents[0].url # TO UPDATE
        messages = self.create_openai_message(context_docs, request.query)
        openai_stream = self.create_openai_stream(messages)

        return self.generate(openai_stream, source_url)

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
        embedding = get_embedding(text_input.text)
        return {"data": embedding}

    def create_openai_message(self, context_docs, query):
        """
        Format the message to send to the OpenAI API.

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
        return [{"role": "system", "content": openai_rag_system_prompt},]

    def create_openai_stream(self, messages):
        """
        Create a stream to communicate with OpenAI.

        Parameters
        ----------
        messages : dict

        Returns
        -------
        chat.completion
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=self.stream,
            temperature=self.temperature,
            top_p=self.top_p)

    def generate(self, openai_stream, source_url):
        """
        Generate the answer using LLM.

        Parameters
        ----------
        openai_stream
        source_url

        Returns
        -------

        """
        for chunk in openai_stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content.encode("utf-8")
            else:
                # Send a special token indicating the end of the response
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode("utf-8")
                return


processor = RAGProcessor(model=rag_config["llm"]["model"],
                         max_token=rag_config["llm"]["max_output_tokens"],
                         stream=rag_config["llm"]["stream"],
                         temperature=rag_config["llm"]["temperature"],
                         top_p=rag_config["llm"]["top_p"],
                         retrieval_method=rag_config["retrieval"]["retrieval_method"],
                         top_k=rag_config["retrieval"]["top_k"],
                         client=clientAI)

