import logging

from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

import csv
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


@app.get("/retriever",
         summary="Eval the accuracy of the retriever",
         response_description="csv file with the results, named with the mean score")
async def retriever(file: UploadFile = File(...), retriever_type: RetrieverType = "top_k retriever", db: Session = Depends(get_db)):
    if retriever_type is RetrieverType.rewrite:
        retriever = QueryRewritingRetriever(processor,3, 5)
    elif retriever_type is RetrieverType.context_compr:
        retriever = ContextualCompressionRetriever(processor, 5)
    else:
        retriever = TopKRetriever(5)

    data = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    embedding_column = "embedding" in data.fieldnames
    language_column = "language" in data.fieldnames

    for row in data:
        embedding = ast.literal_eval(row["embedding"]) if embedding_column else None
        language = row["language"] if language_column else None
        document = DocumentCreate(url=row["url"], text=row["text"], embedding=embedding, source=file.filename, language=language)
        document_service.upsert(db, document, embed=embed)

    np.array(Image.open(BytesIO(data)))
