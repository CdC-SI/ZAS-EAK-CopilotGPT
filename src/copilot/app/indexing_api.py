import logging

from fastapi import FastAPI, status, Depends
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

# Load env variables
from config.base_config import indexing_app_config

# Load utility functions
from indexing.scraper import Scraper

from sqlalchemy.orm import Session
from database.service.question import crud_question
from database.service.document import crud_document
from database.service.source import crud_source
from database.schemas import QuestionCreate, QuestionsCreate, DocumentCreate, DocumentsCreate, SourceCreate
from database.database import get_db

# Load models
from rag.models import ResponseBody

import csv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Create an instance of FastAPI
app = FastAPI(**indexing_app_config)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/add_rag_data_from_csv", summary="Insert data for RAG without embedding from a local csv file", status_code=200, response_model=ResponseBody)
def add_rag_data_from_csv(file_path: str = "indexing/data/rag_test_data.csv", db: Session = Depends(get_db)):
    """
    Add and index test data for RAG from csv files without embeddings.

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    source = crud_source.create(db, SourceCreate(url=file_path))
    with open(file_path, mode='r') as file:
        data = csv.DictReader(file)
        documents = [DocumentCreate(text=row["text"], url=row["url"], source_id=source.id) for row in data]

    crud_document.create_all(db, DocumentsCreate(documents=documents))

    return {"content": "yay"}


@app.post("/add_faq_data_from_csv", summary="Insert data for FAQ without embedding from a local csv file", status_code=200, response_model=ResponseBody)
def add_faq_data_from_csv(file_path: str = "indexing/data/faq_test_data.csv", db: Session = Depends(get_db)):
    """
    Add and index test data for RAG from csv files without embeddings.

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    source = crud_source.create(db, SourceCreate(url=file_path))

    with open(file_path, mode='r') as file:
        data = csv.DictReader(file)
        questions = [QuestionCreate(text=row["text"], url=row["url"], answer=row["answer"], language=row["language"], source_id=source.id) for row in data]

    crud_question.create_all(db, QuestionsCreate(questions=questions))

    return {"content": "yay"}


@app.post("/embed_rag_data", summary="Embed all data for RAG that have not been embedded yet", status_code=200, response_model=ResponseBody)
def embed_rag_data(db: Session = Depends(get_db)):
    """
    Embed all data for RAG that have not been embedded yet.

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    crud_document.embed_all(db)
    return {"content": "yay"}


@app.post("/embed_faq_data", summary="Embed all data for FAQ that have not been embedded yet", status_code=200, response_model=ResponseBody)
def embed_faq_data(db: Session = Depends(get_db)):
    """
    Embed all data for FAQ that have not been embedded yet.

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    crud_question.embed_all(db)
    return {"content": "yay"}


@app.post("/index_rag_vectordb", summary="Insert Embedding data for RAG", response_description="Insert Embedding data for RAG", status_code=200, response_model=ResponseBody)
async def index_rag_vectordb(db: Session = Depends(get_db)):
    """
    Add and index test data for RAG to the embedding database.

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    add_rag_data_from_csv()
    return embed_rag_data()


@app.post("/index_faq_vectordb", summary="Insert Embedding data for FAQ autocomplete semantic similarity search", response_description="Insert Embedding data for FAQ semantic similarity search", status_code=200, response_model=ResponseBody)
def index_faq_vectordb(db: Session = Depends(get_db)):
    """
    Add and index test data for Autocomplete to the FAQ database.

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    add_faq_data_from_csv()
    return embed_faq_data


@app.get("/crawl_data", summary="Crawling endpoint", response_description="Welcome Message")
async def crawl_data():
    """
    Dummy endpoint for data crawling.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/scrap_data/", summary="Scraping Endpoint", response_description="Welcome Message")
async def scrap_data():
    """
    Dummy endpoint for data scraping.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/index_data", summary="Indexing Endpoint", response_description="Welcome Message")
async def index_data():
    """
    Dummy endpoint for data indexing.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/parse_faq_data", summary="FAQ Parsing Endpoint", response_description="Welcome Message")
async def parse_faq_data():
    """
    Dummy endpoint for FAQ data parsing.
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/parse_rag_data", summary="Parsing Endpoint", response_description="Welcome Message")
async def parse_rag_data():
    """
    Dummy endpoint for data parsing (RAG).
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/chunk_rag_data", summary="Chunking Endpoint", response_description="Welcome Message")
async def chunk_rag_data():
    """
    Dummy endpoint for data chunking (RAG).
    """
    return Response(content="Not Implemented", status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.put("/index_faq_data", summary="Insert Data from faq.bsv.admin.ch", response_description="Insert Data from faq.bsv.admin.ch")
async def index_faq_data(sitemap_url: str = 'https://faq.bsv.admin.ch/sitemap.xml', proxy: str = None, k: int = 0):
    """
    Add and index data for Autocomplete to the FAQ database. The data is obtained by scraping the website `sitemap_url`.

    Parameters
    ==========
    sitemap_url : str, default 'https://faq.bsv.admin.ch/sitemap.xml'
        the `sitemap.xml` URL of the website to scrap
    proxy : str, optional
        Proxy URL if necessary
    k : int, default 0
        Number of article to scrap and log to test the method.

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    logging.basicConfig(level=logging.INFO)

    scraper = Scraper(sitemap_url, proxy=proxy)
    urls = await scraper.run(k=k)

    return {"message": f"Done! {len(urls)} wurden verarbeitet."}


@app.put("/data", summary="Update or Insert FAQ Data", response_description="Updated or Inserted Data")
async def index_data(article_in: QuestionCreate, db: Session = Depends(get_db)):
    """
    Upsert a single entry to the FAQ dataset.

    Parameters
    ----------
    article_in : ArticleFAQCreate
        The article id, url, question, answer and language to insert or update
    db : Session
        Database session

    Returns
    -------
    dict
        The article id, url, question, answer and language upon successful completion of the process
    """
    return crud_question.create_or_update(db, article_in)
