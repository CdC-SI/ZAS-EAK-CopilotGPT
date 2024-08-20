import logging

from fastapi import FastAPI, Depends, File, UploadFile, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

import csv
import io
import ast
import numpy as np
import codecs

from enum import Enum
from rag.retrievers import Reranker, TopKRetriever, QueryRewritingRetriever, ContextualCompressionRetriever, RAGFusionRetriever
from rag.rag_processor import llm_client
from sklearn.metrics import ndcg_score

from sqlalchemy.orm import Session
from database.database import get_db
from schemas.document import Document

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create required class instances
app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RetrieverType(str, Enum):
    top_k = "top-K retriever"
    rewrite = "query rewriting retriever"
    context_compr = "contextual compression retriever"
    fusion = "RAG fusion retriever"


class EvalMetric(str, Enum):
    recall_at_k = "Recall@k"
    ndcg = "Normalized Discounted Cumulative Gain (NDCG)"


class RerankModel(str, Enum):
    multi_v3 = "rerank-multilingual-v3.0"
    multi_v2 = "rerank-multilingual-v2.0"
    eng_v3 = "rerank-english-v3.0"
    eng_v2 = "rerank-english-v2.0"


def format_string(s: str):
    return ' '.join(s.split())


@app.post("/retriever",
         summary="Eval the accuracy of the retriever",
         response_description="csv file with the results, named with the mean score")
async def retriever(file: UploadFile = File(...),
                    retriever_type: RetrieverType = "top_k retriever",
                    rerank_model: RerankModel = None,
                    metric: EvalMetric = "Recall@k",
                    db: Session = Depends(get_db)):
    """
    Evaluate the accuracy of the requested retriever. The mean recall score is given in the name of the CSV file.

    Parameters
    ----------
    file: UploadFile
        CSV file containing the questions to evaluate and the expected answers
    retriever_type: RetrieverType
        Type of retriever to evaluate
    rerank_model: RerankModel
        Reranker model to use
    metric: EvalMetric
        Metric to use for evaluation
    db: Session
        Database session

    Returns
    -------
    StreamingResponse
        CSV file with the results, named with the mean score
    """
    k = 5

    # Initialise the retriever
    if retriever_type is RetrieverType.rewrite:
        retriever = QueryRewritingRetriever(3, k, llm_client)
    elif retriever_type is RetrieverType.context_compr:
        retriever = ContextualCompressionRetriever(k, llm_client)
    elif retriever_type is RetrieverType.fusion:
        retriever = RAGFusionRetriever(llm_client, top_k=k)
    else:
        retriever = TopKRetriever(k)

    reranker = None
    if rerank_model:
        reranker = Reranker(rerank_model, k)

    # Read the data
    data_iter = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))

    # Compute dtype for structured numpy array
    dtype = np.dtype([("recall", "<f8"), ("query", "U200"), ("y_true", "O"), ("retrieved_answers", "O")])

    data = []
    total_score = 0

    for row in data_iter:
        query, true_answers = row["query"], format_string(row["y_true"])

        try:
            true_answers = ast.literal_eval(true_answers)
        except:
            true_answers = [true_answers]

        # Retrieve the documents
        retrieved_answers = retriever.get_documents(db, query, k=k)
        retrieved_answers = [format_string(doc.text) for doc in retrieved_answers]
        if reranker:
            retrieved_answers = reranker.rerank(query, retrieved_answers)

        # Compute metrics
        if metric is EvalMetric.ndcg:
            y_true = [1 if answer in true_answers else 0 for answer in retrieved_answers]
            y_score = [i for i in range(k, 0, -1)]
            score = ndcg_score([y_true], [y_score])
        else:
            score = sum([true_answer in retrieved_answers for true_answer in true_answers]) / len(true_answers)
        total_score += score

        data.append((score, query, true_answers, retrieved_answers))

    # Write the data to a stream
    data_array = np.array(data, dtype=dtype)

    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(data_array.dtype.names)  # Write header
    for row in data_array:
        writer.writerow(row)

    stream.seek(0)
    response = StreamingResponse(stream, media_type="text/csv")

    response.headers["Content-Disposition"] = f"attachment; filename=recall_{total_score/len(data):.4f}.csv"
    return response

