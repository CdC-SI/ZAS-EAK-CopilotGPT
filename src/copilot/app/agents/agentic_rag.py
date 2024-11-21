import os
from dotenv import load_dotenv

import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

import sys
sys.path.append("../../app")
from config.clients_config import clientLLM

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)

POSTGRES_USER = os.environ.get("POSTGRES_USER", None)
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
POSTGRES_HOST = "localhost"
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", None)
POSTGRES_DB = os.environ.get("POSTGRES_DB", None)

def connect_to_db() -> Session:
    """
    Connect to the database using provided parameters

    Parameters
    ----------
    user : str
        Database user
    password : str
        Database password
    host : str
        Database host
    port : int
        Database port
    database : str
        Database name

    Returns
    -------
    Session
    """
    db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(db_url, future=True, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

db = connect_to_db()

from rag.retrievers import RetrieverClient, TopKRetriever
from rag.reranker import Reranker

retrievers = [TopKRetriever(top_k=10)]
reranker = Reranker(model="rerank-multilingual-v3.0",
                    top_k=5)


retriever_client = RetrieverClient(retrievers=retrievers,
                            reranker=reranker)

# Define the maximum number of retrieval cycles
MAX_RETRIEVAL_CYCLES = 3

# Define the QueryHandler class
class QueryHandler:
    def __init__(self):
        pass

    async def assess_topic(self, query):
        # Placeholder for topic assessment logic
        topic_kws = ["avs", "avs21", "ai", "ahv", "iv", "familienzulagen"]
        query = query.replace("?", "").replace("-", " ")
        query_kws = query.split()
        is_on_topic = any(word.lower() in topic_kws for word in query_kws)
        print("Assessing if query is on-topic.")
        return is_on_topic

    async def ask_for_clarification(self):
        # Placeholder for asking the user for clarification
        refined_query = "User's clarified query"
        print("Assistant: Could you please clarify your question?")
        print(f"User: {refined_query}")
        return refined_query

# Define the DocumentEvaluation class
class DocumentEvaluation(BaseModel):
    relevant: bool

# Define the AgentEvaluator class
class AgentEvaluator:
    def __init__(self):
        self.llm_client = clientLLM

    async def evaluate_document(self, document, query):
        # Placeholder for document evaluation logic
        prompt = """You are an expert document relevancy evaluator. Evaluate if the document can answer the query.

        Return True if the document is relevant to the query and False otherwise.

        DOCUMENT: {document}

        QUERY: {query}"""
        messages = [{"role": "system", "content": prompt.format(document=document, query=query)},]
        res = await self.llm_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                temperature=0,
                top_p=0.95,
                max_tokens=2048,
                messages=messages,
                response_format=DocumentEvaluation
            )
        is_relevant = res.choices[0].message.parsed.relevant
        if is_relevant:
            return document
        else:
            return None

    async def assess_sufficiency(self, query, relevant_documents):
        # Placeholder for sufficiency assessment logic
        prompt = """You are an expert in AHV/IV, AVS/AI (social insurances in Switzerland). Evaluate if the documents are sufficient to answer the query. You can only answer True after a thorough analysis of the documents, and ONLY if they contain ALL necessary relevant information to answer the query.

        Return True if the documents are sufficient to answer the query and False otherwise.

        DOCUMENTS:

        {relevant_documents}

        QUERY: {query}"""
        messages = [{"role": "system", "content": prompt.format(relevant_documents="\n\n".join([doc['text'] for doc in relevant_documents]), query=query)},]
        res = await self.llm_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                temperature=0,
                top_p=0.95,
                max_tokens=2048,
                messages=messages,
                response_format=DocumentEvaluation
            )
        is_sufficient = res.choices[0].message.parsed.relevant
        print("Assessing sufficiency of documents.")
        return is_sufficient

    async def decide_query_refinement(self, query, full_documents):
        # Placeholder for agent's decision-making logic
        prompt = """You are an expert query refiner evaluator. Your task is to determine whether the user query can be refined based on the documents retrieved in the first document retrieval round in a RAG system. You must decide if the query can be improved based on the vocabulary, terms, terminology, phrasology in the retrieved documents in a semantic search setting. The query must be semantically similar to the documents, and your task is to determine if this can be improved. Evaluate if the query can be refined.

        Return True if the query can be refined and False otherwise.

        RETRIEVED DOCUMENTS: {document}

        QUERY: {query}"""
        messages = [{"role": "system", "content": prompt.format(document=full_documents, query=query)},]
        res = await self.llm_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                temperature=0,
                top_p=0.95,
                max_tokens=2048,
                messages=messages,
                response_format=DocumentEvaluation
            )
        agent_can_refine = res.choices[0].message.parsed.relevant
        print("Deciding whether to refine query autonomously.")
        if agent_can_refine:
            return True
        else:
            return False


# Define the QueryRefiner class
class QueryRefiner:
    def __init__(self):
        self.llm_client = clientLLM

    async def refine_query(self, query, full_documents):
        # Placeholder for query refinement logic
        prompt = """You are an expert query refiner. Your task is to refine the query taking into account the documents retrieved in the first retrieval round. Improve query vocabulary and formulation for a semantic search setting.


        RETRIEVED DOCUMENTS: {document}

        QUERY: {query}

        REFINED QUERY:"""
        messages = [{"role": "system", "content": prompt.format(relevant_documents="\n\n".join([doc['text'] for doc in full_documents]), query=query)},]
        res = await self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                stream=False,
                temperature=0,
                top_p=0.95,
                max_tokens=2048,
                messages=messages,
            )
        refined_query = res.choices[0].message.content
        print(f"Refining query: {refined_query}")
        return refined_query

# Define the AnswerGenerator class
class AnswerGenerator:
    def __init__(self):
        self.llm_client = clientLLM

    async def generate_answer(self, query, relevant_documents):
        # Placeholder for answer generation logic
        prompt = """You are a helpful AI assistant. Use the context documents to answer the query.

        CONTEXT DOCUMENTS:

        {relevant_documents}

        QUERY: {query}"""
        messages = [{"role": "system", "content": prompt.format(relevant_documents="\n\n".join([doc['text'] for doc in relevant_documents]), query=query)},]
        res = await self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                stream=False,
                temperature=0,
                top_p=0.95,
                max_tokens=2048,
                messages=messages,
            )
        answer = res.choices[0].message.content
        return answer

# Define the WorkflowManager class
class WorkflowManager:
    def __init__(self):
        self.query_handler = QueryHandler()
        self.retriever = retriever_client
        self.evaluator = AgentEvaluator()
        self.refiner = QueryRefiner()
        self.answer_generator = AnswerGenerator()
        self.retrieval_round = 0

    async def run_workflow(self, query):
        # Step 0: User Query Input and Topic Assessment
        is_on_topic = await self.query_handler.assess_topic(query)

        if not is_on_topic:
            # Return answer to frontend/uas-security
            print("Assistant: How can I can I help you with matters related to AVS/AI?")
            return

        # Initialize variables
        sufficient_documents = False

        # Main retrieval and evaluation loop
        while not sufficient_documents and self.retrieval_round < MAX_RETRIEVAL_CYCLES:
            self.retrieval_round += 1
            print(f"\n--- Retrieval Round {self.retrieval_round} ---")

            # Step 1: Initial Document Retrieval
            # NEED TO CACHE/REMOVE ALREADY RETRIEVED DOCUMENTS !!!
            documents = await self.retriever.get_documents(db, query, k=10)

            # Step 2: Agent Evaluation of Retrieved Documents
            evaluation_tasks = [self.evaluator.evaluate_document(doc, query) for doc in documents]
            evaluation_results = await asyncio.gather(*evaluation_tasks)
            relevant_chunks = [result for result in evaluation_results if result is not None]

            # Retrieve remaining chunks to reconstruct full documents (placeholder)
            #full_documents = ["full_document_from_chunk_1"]  # Simulate assembling full documents
            # Will have to do URL injection here + KG + PageRank consolidation
            full_documents = relevant_chunks

            # Step 3: Assess Sufficiency of Documents
            sufficient_documents = await self.evaluator.assess_sufficiency(query, full_documents)

            if sufficient_documents:
                # Step 6: Answer Generation
                answer = await self.answer_generator.generate_answer(query, full_documents)
                print(f"Assistant: {answer}")
                return
            else:
                # Step 4: Query Refinement
                agent_can_refine = await self.evaluator.decide_query_refinement(query, full_documents)
                if agent_can_refine:
                    # Agent refines the query autonomously
                    query = await self.refiner.refine_query(query, full_documents)
                else:
                    # Agent asks the user for clarification
                    # EITHER USE TOOL OR ASK GENERIC QUESTION OR ASK QUESTION BASED ON RETRIEVED CONTENT AND CURRENT QUERY
                    query = await self.query_handler.ask_for_clarification()

        # Step 7: Handling Insufficient Information
        print("Assistant: I'm sorry, I cannot answer your query with the available data.")

# Main execution
async def main():
    workflow_manager = WorkflowManager()

    #query = "wer ist donald Trump?"
    #query = "avs21 expliqué en une phrase"
    #query = "ich, weiblich, geboren 31.12.1962. Wann erhalte ich meine erste AHV Rente?"
    query = "ich arbeite vollzeit (100%), und die kinder leven bei meiner arbeitslosen ex partnerin. Wer erhält in diesem Fall die Familienzulagen?"

    await workflow_manager.run_workflow(query)

# Run the asynchronous main function
asyncio.run(main())
