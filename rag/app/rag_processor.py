import httpx

from config.openai_config import openai

from rag.app.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE
from rag.app.models import RAGRequest, EmbeddingRequest

from autocomplete.app.queries import semantic_similarity_match
from utils.embedding import get_embedding


class RAGProcessor:
    def __init__(self, rag_config):
        self.rag_config = rag_config
        self.client = openai.OpenAI()

        self.k_retrieve = rag_config["retrieval"]["top_k"]

    async def retrieve(self, request: RAGRequest, language: str = '*', k: int = None):
        # Only supports retrieval of 1 document at the moment (set in /config/config.yaml). Will implement multi-doc retrieval later
        k = self.k_retrieve if k is None else k

        rows = await semantic_similarity_match(request.query, db_name='embeddings', language=language, k=k)
        documents = [dict(row) for row in rows][0]

        return {"contextDocs": documents["text"], "sourceUrl": documents["url"], "cosineSimilarity": documents["cosine_similarity"]}

    async def process(self, request: RAGRequest):
        json_response = await self.fetch_context_docs(request.query)
        context_docs = json_response['contextDocs']
        source_url = json_response['sourceUrl']
        messages = self.create_openai_message(context_docs, request.query)
        openai_stream = self.create_openai_stream(messages)

        return self.generate(openai_stream, source_url)

    async def embed(self, text_input: EmbeddingRequest):
        embedding = get_embedding(text_input.text)[0].embedding
        return {"data": embedding}

    async def fetch_context_docs(self, query):
        async with httpx.AsyncClient() as client:
            response = await client.post("http://rag:8010/rag/docs", json={"query": query})
        response.raise_for_status()
        return response.json()

    def create_openai_message(self, context_docs, query):
        openai_rag_system_prompt = OPENAI_RAG_SYSTEM_PROMPT_DE.format(context_docs=context_docs, query=query)
        return [{"role": "system", "content": openai_rag_system_prompt},]

    def create_openai_stream(self, messages):
        return self.client.chat.completions.create(
            model=self.rag_config["llm"]["model"],
            messages=messages,
            max_tokens=self.rag_config["llm"]["max_output_tokens"],
            stream=self.rag_config["llm"]["stream"],
            temperature=self.rag_config["llm"]["temperature"],
            top_p=self.rag_config["llm"]["top_p"]
        )

    def generate(self, openai_stream, source_url):
        for chunk in openai_stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content.encode("utf-8")
            else:
                # Send a special token indicating the end of the response
                yield f"\n\n<a href='{source_url}' target='_blank' class='source-link'>{source_url}</a>".encode("utf-8")
                break