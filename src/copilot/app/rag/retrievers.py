from rag.base import BaseRetriever
from rag.prompts import QUERY_REWRITING_PROMPT
from database.service import document_service

from concurrent.futures import ThreadPoolExecutor, as_completed

class RetrieverClient(BaseRetriever):
    """
    A client for retrieving documents using multiple retrieval strategies in parallel.

    The `RetrieverClient` class manages a collection of retrievers and executes their
    `get_documents` methods in parallel, aggregating the results into a single list of documents.

    Parameters
    ----------
    retrievers : list
        A list of retriever instances that implement the `get_documents` method. These retrievers
        are executed in parallel to retrieve documents based on the specified query.

    Methods
    -------
    get_documents(db, query, language, k)
        Retrieves documents from the database using the provided query, language and returns top k documents. The results are aggregated into a single list of documents.

    """
    def __init__(self, retrievers):
        self.retrievers = retrievers

    def get_documents(self, db, query, language, k):
        """
        Retrieve documents using multiple retrievers in parallel.

        This method executes the `get_documents` method of each retriever in parallel using a
        ThreadPoolExecutor. The results from all retrievers are aggregated into a single list,
        which is then returned. If any retriever raises an exception, it is caught and logged,
        but the retrieval process continues for the remaining retrievers.

        Parameters
        ----------
        db : Any
            The database connection or session object used by the retrievers to query documents.
        query : str
            The search query used to retrieve relevant documents.
        language : str
            The language in which the documents are retrieved.
        k : int
            The number of top documents to retrieve from each retriever.

        Returns
        -------
        docs : list
            A list of documents retrieved from the database, aggregated from all the retrievers.

        Raises
        ------
        None
            Exceptions raised by individual retrievers are caught and logged, not propagated.
        """
        docs = []

        with ThreadPoolExecutor() as executor: # Use ThreadPoolExecutor for parallel execution
            future_to_retriever = {
                executor.submit(retriever.get_documents, db, query, language, k): retriever
                for retriever in self.retrievers
            }

            for future in as_completed(future_to_retriever): # Collect results as they complete
                retriever = future_to_retriever[future]
                try:
                    result = future.result()
                    docs.extend(result)
                except Exception as e:
                    print(f"Retriever {retriever} raised an exception: {e}")

        return docs

class TopKRetriever(BaseRetriever):
    """
    A class used to retrieve the top K documents that semantically match a given query.

    Methods
    -------
    get_documents(db, query, language, k)
        Retrieves the top k documents that semantically match the given query.
    """
    def __init__(self):
        pass

    def get_documents(self, db, query, language, k):
        """
        Retrieves the top K documents that semantically match the given query.

        Parameters
        ----------
        db : object
            The database object where the documents are stored.
        query : str
            The query to match.
        language : str
            The language of the query.
        k : int
            The number of documents to retrieve.

        Returns
        -------
        list
            A list of the top k documents that semantically match the query.
        """
        docs = document_service.get_semantic_match(db, query, language=language, k=k)
        return docs

class QueryRewritingRetriever(BaseRetriever):

    def __init__(self):
        self.top_k_retriever = TopKRetriever()

    def get_documents(self, db, query, language, k):

        # QUERY_REWRITING_PROMPT
        rewritten_queries = []

        docs = []
        for query in rewritten_queries:
            query_docs = document_service.get_semantic_match(db, query, language=language, k=k)
            docs.extend(query_docs)

        return docs

class ContextualCompressionRetriever(BaseRetriever):
    pass

class RAGFusionRetriever(BaseRetriever):
    pass

class BM25Retriever(BaseRetriever):
    config: Dict[str, Any]
    index: Optional[Index]
    k: Optional[float] = 1.2
    b: Optional[float] = 0.75
    top_k: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pinecone_init()
        self.index = pinecone.Index(self.config['index']['name'])
        self.k = self.config['retrieval']['bm25']['k']
        self.b = self.config['retrieval']['bm25']['b']
        self.top_k = self.config['retrieval']['bm25']['top_k']

    def pinecone_init(self):
        """
        Initializes the Pinecone client with the provided API key and environment.

        This method uses the global variables PINECONE_API_KEY and PINECONE_ENVIRONMENT to initialize the Pinecone client. These variables should be set in the environment where this code is running.
        """
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT
        )

    def bm25_score(self, query: str, docs: List[Document]) -> np.array:

        doc_len = np.array([len(x.page_content) for x in docs])
        avg_doc_len = np.mean(doc_len)
        n_docs = len(docs)
        freq = np.array([doc.page_content.count(query) for doc in docs])

        tf = np.array((freq * (1 + self.k)) / (freq + self.k * (1 - self.b + self.b * doc_len / avg_doc_len)))
        N_q = sum([1 for doc in docs if query in doc])
        idf = np.log(((n_docs - N_q + 0.5) / (N_q + 0.5)) + 1)

        return tf * idf

    def get_relevant_documents(self, query: str, token: str) -> List[Document]:

        # get documents from database
        n_vectors = self.index.describe_index_stats()['namespaces'][self.config['index']['base-namespace']]['vector_count']
        res = self.index.query(
                vector=[0] * 768, # dummy vector, embedding dim
                top_k=n_vectors,
                namespace=self.config['index']['base-namespace'],
                include_values=False,
                include_metadata=True,
                )

        docs = [Document(page_content=x['metadata']['text'], metadata=x['metadata']) for x in res['matches']]

        # compute bm25 score
        scores = self.bm25_score(query, docs)

        # sort retrieved context docs according to score
        top_docs = list(sorted(zip(docs, scores), key=lambda x: x[1], reverse=True))[:self.top_k]

        # Make the score part of the document metadata
        docs = []
        for doc in top_docs:
            docs.append(Document(page_content=doc[0].page_content, metadata={"bm_25_score": doc[1]}))

        return docs

class Reranker(BaseRetriever):
    pass