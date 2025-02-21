# Copilot architecture

## Overall Architecture (High-Level)
```mermaid
flowchart LR
  %% Docker Compose Infrastructure
  subgraph "Docker Compose Services"
    DB[PostgreSQL<br/>Database]
    COP["copilot API<br/>(FastAPI Python)"]
    SEC["zas-security<br/>Service"]
    FRONT["zas-copilot<br/>Frontend"]
    LANG["Langfuse<br/>Logging Service"]
    REDIS["Redis<br/>Cache"]
  end

  %% Copilot Application Modules
  subgraph "Copilot Application Modules" [Copilot Application]
    CHAT["chat_api"]
    RAG["rag_api"]
    INDEX["indexing_api"]
    AUTO["autocomplete_api"]
    CMD["command_api"]
    CONV["conversations_api"]
    SET["settings_api"]
  end

  %% Interconnections between infrastructure and modules

  %% The copilot container hosts the main application modules
  COP --> CHAT
  COP --> RAG
  COP --> INDEX
  COP --> AUTO
  COP --> CMD
  COP --> CONV
  COP --> SET

  %% Copilot container connects to external services
  COP --> DB
  COP --> REDIS

  %% Supporting services and interactions
  SEC --- COP
  FRONT --- SEC
  LANG --- SEC

  %% (Optional) High-level interaction amongst internal modules:
  CHAT ---|uses context| RAG
```

The “Docker Compose Services” subgraph represents the core infrastructure:
- Database (PostgreSQL DB)
- copilot API container (which runs the core FastAPI application)
- zas-security (the backend security service)
- zas-copilot (the frontend service for the Copilot application)
- Langfuse (used for logging/observability)
- Redis (used as an in-memory cache)

Within the copilot API container, there is a “Copilot Application Modules” subgraph representing the main functional modules:
- chat_api
- rag_api
- indexing_api
- autocomplete_api
- command_api
- conversations_api
- settings_api

The copilot container interacts with the database and Redis for persistence and caching.
- The security service (zas-security) and the frontend (zas-copilot) interact with the copilot container.
- Langfuse is connected to the security service for logging/observability.
- Internally, some modules interact.

## Chat Processing Pipeline
```mermaid
flowchart TD
    A[Incoming Chat Request<br/>chat_api]
    B[ChatBot]
    C[LLM Factory<br/>& MessageBuilder]
    D[Memory Service<br/>Buffer/Buffersummary]
    E[Chat Processing]
    F1[Vanilla LLM Processing]
    F2[Command Processing]
    F3[RAG Processing]
    F4[Agentic RAG Processing]
    G[Conversation Turn Indexing<br/>store user & assistant messages]
    H[(PostgreSQL DB)]

    A --> B
    B --> C
    B --> D
    B --> E
    E --> F1
    E --> F2
    E --> F3
    E --> F4
    F1 --> G
    F2 --> G
    F3 --> G
    F4 --> G
    G --> H
```

## Retrieval Pipeline
```mermaid
flowchart TD
    A[Start Retrieval Request]
    B[RAG Service]
    C[Memory Service<br/>retrieve conversation context]
    D[RetrieverFactory]
    E1[Top-K Retriever]
    E2[Query Rewriting Retriever]
    E3[Contextual Compression Retriever]
    E4[BM25 Retriever]
    E5[etc.]
    F[Aggregator: RetrieverClient<br/>combine results]
    G[Optional: Reranker]
    H[LLM Processing<br/>generate messages via MessageBuilder]
    I[Output Streaming]

    A --> B
    B --> C
    B --> D
    D --> E1
    D --> E2
    D --> E3
    D --> E4
    D --> E5
    E1 --> F
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F
    F --> G
    G --> H
    H --> I
```

# Copilot workflows

## Autocomplete
```mermaid
flowchart TD
    A[Start Autocomplete Request] --> B[Call Trigram Match Function]
    A --> C[Call Fuzzy Match Function]
    B & C --> D[Combine Exact & Fuzzy Matches]
    D --> E{Question ends with '?'}
    E -- Yes --> F[Check Semantic Similarity Match]
    F --> G[Cache Semantic Results]
    E -- No --> H[Skip Semantic Matching]
    H --> I[Return Combined Matches]
    G --> I
```

## RAG
```mermaid
flowchart TD
    A[Start RAG Request] --> B[Retrieve Documents]
    B --> C{Retrieval Methods}
    C --> C1[Semantic Matching]
    C --> C2[BM25]
    C --> C3[Query Rewriting]
    C --> C4[etc.]
    C1 --> D[Aggregate Retrieved Results]
    C2 --> D
    C3 --> D
    C4 --> D
    D --> E{Reranking enabled?}
    E -- Yes --> F[Rerank Documents]
    E -- No --> G[Use Aggregated Documents]
    F --> G
    G --> H{Source Validation Enabled?}
    H -- Yes --> I[Validate & Filter Sources]
    H -- No --> J[Skip Validation]
    I --> K[Combine Validated Documents]
    J --> K
    K --> L[Call LLM with Combined Documents]
    L --> M[Generate Streaming Tokens]
    M --> N[Return Streaming Response]
```

## Agentic RAG

```mermaid
flowchart TD
    A[Start Agentic RAG Request] --> B[Intent Detection]
    B --> |Followup generated| C[Return Followup Question & Stop]
    B --> |No followup| D[Infer Sources and optionally Tags]
    D --> E[Agent Handoff: Select appropriate Agent]
    E --> F[Pass Request to Chosen Agent]
    F --> G[Agent Processes Request<br>Tool call</br>]
    G --> H[Generate Streaming Response]
    H --> I[Return Response]
```

## Indexing
```mermaid
flowchart TD
    A[Start Indexing Process] --> B[Scrape Data]
    B --> C[Parse & Clean Documents]
    C --> D[Database Upsertion via document_service.upsert]
    D --> E[Indexing Complete]
```
