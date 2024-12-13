# Release history

### main branch

### ZAS-EAK-CopilotGPT v0.3.0

- Integrate Ollama LLMs
- Add login check for advanced functionality use
- Add topic check for agentic rag
- Add source validation for rag / agentic rag
- Send status updates via SSE (eg. <source>, <routing>, <retrieving>, <agent_handoff>, <tool_use>, etc.)
- Implement Pension Agent, RAG Agent
- Implement /summarize, /translate commands
- Refactor API routes
- Refactor prompts
- Display project version in frontend
- Add new configuration options in frontend (LLM, Retrieval, Chat, Answer Style)
- Add Einfache/Leichte Sprache answer style
- Add condensed/complete answer styles
- Fix RAGFusionRetriever bug
- Fix chat history indexing bug

- Note: runs with copilot-frontend at `https://github.com/CdC-SI/copilot-frontend/commits/command-highlightinh#261164eecb53c8395566426b5f610753c67c83e1`
- Note: runs with copilot-backend at `https://github.com/CdC-SI/copilot-backend/commits/commands#1a07c98b17360308b27f986adaf7d57b795ab829`

### ZAS-EAK-CopilotGPT v0.2.0

- Integrate `llama.cpp` llm models

### ZAS-EAK-CopilotGPT v0.1.0

- GUI
    - Autocomplete/RAG functionality in chatbar
    - Chat history
    - Chat parameters
    - Administration panel for Survey Pipeline
- Authentication
- Autocomplete
- RAG
    - Retrievers + reranker
    - Commercial API LLMs (OpenAI, AzureOpenAI, Anthropic, Groq)
    - OS API LLMs (MLX)
- Indexing (*.admin.ch, ahv-iv.ch)
- LLM Observability tool
- Conversational memory
- Chat history indexing
