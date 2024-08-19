import logging

from fastapi import FastAPI, Depends, File, UploadFile, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

import csv
import io
import numpy as np
import codecs
import json
from enum import Enum
from rag.retrievers import TopKRetriever, QueryRewritingRetriever, ContextualCompressionRetriever, RAGFusionRetriever
from rag.rag_processor import llm_client

from sqlalchemy.orm import Session
from database.database import get_db

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


def format_string(s: str):
    return ' '.join(s.split())


@app.post("/retriever",
         summary="Eval the accuracy of the retriever",
         response_description="csv file with the results, named with the mean score")
async def retriever(file: UploadFile = File(...), retriever_type: RetrieverType = "top_k retriever", db: Session = Depends(get_db)):
    """
    Evaluate the accuracy of the requested retriever. The mean recall score is given in the name of the CSV file.

    Parameters
    ----------
    file: UploadFile
        CSV file containing the questions to evaluate and the expected answers
    retriever_type: RetrieverType
        Type of retriever to evaluate
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

    # Read the data
    data_iter = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))

    # Compute dtype for structured numpy array
    answer_dtype = [(f"retrieved_answer_{i}", "U1000") for i in range(k)]
    dtype = np.dtype([("recall", "<i4"), ("query", "U200"), ("y_true", "U1000")] + answer_dtype)

    data = []
    total_recall = 0
    for row in data_iter:
        query, true_answer = row["query"], format_string(row["y_true"])

        # Retrieve the documents
        retrieved_answers = retriever.get_documents(db, query, '', k)
        answers = [format_string(doc.text) for doc in retrieved_answers]

        # Compute recall
        recall = 1 if true_answer in answers else 0
        total_recall += recall

        data.append((recall, query, true_answer) + tuple(answers))

    # Write the data to a stream
    data_array = np.array(data, dtype=dtype)

    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(data_array.dtype.names)  # Write header
    for row in data_array:
        writer.writerow(row)

    stream.seek(0)
    response = StreamingResponse(stream, media_type="text/csv")

    response.headers["Content-Disposition"] = f"attachment; filename=recall_{total_recall/len(data):.4f}.csv"
    return response

