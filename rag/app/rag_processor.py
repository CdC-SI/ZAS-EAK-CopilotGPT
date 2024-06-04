import httpx
from config.openai_config import openai
from rag.app.prompts import OPENAI_RAG_SYSTEM_PROMPT_DE


class RAGProcessor:
    def __init__(self, rag_config):
        self.rag_config = rag_config
        self.client = openai.OpenAI()

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