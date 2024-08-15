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
from rag.retrievers import TopKRetriever, QueryRewritingRetriever, ContextualCompressionRetriever
from rag.rag_processor import processor

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


@app.post("/retriever",
         summary="Eval the accuracy of the retriever",
         response_description="csv file with the results, named with the mean score")
async def retriever(file: UploadFile = File(...), retriever_type: RetrieverType = "top_k retriever", db: Session = Depends(get_db)):
    """
    Evaluate the accuracy of the requested retriever

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

    if retriever_type is RetrieverType.rewrite:
        retriever = QueryRewritingRetriever(processor,3, k)
    elif retriever_type is RetrieverType.context_compr:
        retriever = ContextualCompressionRetriever(processor, k)
    else:
        retriever = TopKRetriever(k)

    data_iter = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))

    data = [data for data in data_iter]
    data_array = np.asarray(data)

    for row in data_array:
        retrieved_answer = retriever.get_documents(db, row["query"], '', k)
        answers = [doc.answer for doc in retrieved_answer]

        row["retrieved_answer"] = answers

    stream = io.StringIO()
    np.savetxt(stream, data_array, delimiter=",", fmt='%s')
    response = StreamingResponse(iter([stream.getvalue()]),
                                 media_type="text/csv"
                                 )

    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response

