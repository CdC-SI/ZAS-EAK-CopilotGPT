import os

from fastapi import FastAPI, Depends, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS
from pathlib import Path

# Load env variables
from config.config import IndexingConfigApp

# Load utility functions
from indexing.from_csv import CreateService, add_data_from_upload
from indexing.pipelines.admin import admin_indexer
from indexing.pipelines.ahv import ahv_indexer
from indexing.pipelines.bsv import BSVIndexer

from database.service.question import question_service
from database.service.document import document_service
from schemas.question import Question, QuestionItem

from database.database import get_db, Session

import tempfile
import shutil

from utils.logging import get_logger
logger = get_logger(__name__)


# Create an instance of FastAPI
app = FastAPI(**IndexingConfigApp)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload_csv_rag", summary="Upload a CSV file for RAG data", status_code=200)
def upload_csv_rag(file: UploadFile = File(...), embed: bool = False, db: Session = Depends(get_db)):
    """
    Upload a CSV file containing RAG data to the database with optional embeddings.
    Please refer to the pydantic models `DocumentCreate` for the expected fields.

    Parameters
    ----------
    file : UploadFile
        The CSV file sent by the user
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    db : Session
        Database session

    Returns
    -------
    Response
        A confirmation message upon successful completion of the process.
    """
    n_entries = add_data_from_upload(file, db, CreateService.RAG, embed)
    return {"message": f"Successfully added {n_entries} entries to RAG database."}


@app.post("/upload_csv_faq", summary="Upload a CSV file for FAQ data", status_code=200)
def upload_csv_faq(file: UploadFile = File(...), embed: bool = False, db: Session = Depends(get_db)):
    """
    Upload a CSV file containing RAG data to the database with optional embeddings.
    Please refer to the pydantic models `QuestionCreate` for the expected fields.

    Parameters
    ----------
    file : UploadFile
        The CSV file sent by the user
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    db : Session
        Database session

    Returns
    -------
    Response
        Confirmation message upon successful completion of the process.
    """
    n_entries = add_data_from_upload(file, db, CreateService.FAQ, embed)
    return {"message": f"Successfully added {n_entries} entries to FAQ database."}


@app.post("/upload_pdf_rag", summary="Upload a PDF file for RAG data", status_code=200)
async def upload_pdf_rag(file: UploadFile = File(...), embed: bool = False, db: Session = Depends(get_db)):
    """
    Upload a CSV file containing RAG data to the database.

    Parameters
    ----------
    file : UploadFile
        The PDF file sent by the user
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    db : Session
        Database session

    Returns
    -------
    Response
        Confirmation message upon successful completion of the process.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_filename = temp_file.name
        shutil.copyfileobj(file.file, temp_file)

    await ahv_indexer.add_content_to_db(db, content=[Path(temp_filename)], source=file.filename, embed=embed)

    os.remove(temp_filename)

    return {"message": f"{file.filename}: PDF file indexed successfully"}


@app.post("/embed_rag_data", summary="Embed all data for RAG that have not been embedded yet", status_code=200)
def embed_rag_data(db: Session = Depends(get_db), embed_empty_only: bool = True, k: int = 0):
    """
    Embed all RAG data (documents) that have not been embedded yet.

    Parameters
    ----------
    db : Session
        Database session
    embed_empty_only : bool, optional
        Embed only data that have not been embedded yet. Defaults to True.
    k : int, optional
        Number of questions to embed. Default to 0 which means all questions.

    Returns
    -------
    Response
        Confirmation message upon successful completion of the process
    """
    document_service.embed_many(db, embed_empty_only, k)
    return {"message": "Successfully embedded all RAG data"}


@app.post("/embed_faq_data", summary="Embed all data for FAQ that have not been embedded yet", status_code=200)
def embed_faq_data(db: Session = Depends(get_db), embed_empty_only: bool = True, k: int = 0):
    """
    Embed all FAQ questions that have not been embedded yet.

    Parameters
    ----------
    db : Session
        Database session
    embed_empty_only : bool, optional
        Embed only data that have not been embedded yet. Defaults to True.
    k : int, optional
        Number of questions to embed. Default to 0 which means all questions.

    Returns
    -------
    Response
        Confirmation message upon successful completion of the process
    """
    question_service.embed_many(db, embed_empty_only, k)
    return {"message": "Successfully embedded all FAQ data"}


@app.post("/index_pdfs_from_sitemap",
          summary="Index memento PDFs from the https://www.ahv-iv.ch/de/Sitemap-DE sitemap",
          response_description="Confirmation message upon successful indexing",
          status_code=200)
async def index_pdfs_from_sitemap(sitemap_url: str = "https://www.ahv-iv.ch/de/Sitemap-DE", embed: bool = False, db: Session = Depends(get_db)):
    """
    Indexes PDFs from a given sitemap URL. The PDFs are scraped and their data is added to the
    embedding database. This function is specifically designed for the site "https://www.ahv-iv.ch".

    Parameters
    ----------
    sitemap_url : str, optional
        The URL of the sitemap to scrape PDFs from. Defaults to "https://www.ahv-iv.ch/de/Sitemap-DE".
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    db : Session
        Database session

    Returns
    -------
    Response
        Confirmation message upon successful completion of the process.
    """
    docs = await ahv_indexer.index(sitemap_url, db, embed=embed)
    return {"message": f"Successfully indexed {len(docs)} PDFs from the {sitemap_url}"}


@app.post("/index_html_from_sitemap",
          summary="Index HTML from a sitemap",
          response_description="Confirmation message upon successful indexing",
          status_code=200)
async def index_html_from_sitemap(sitemap_url: str = "https://eak.admin.ch/eak/de/home.sitemap.xml", embed: bool = False, db: Session = Depends(get_db)):
    """
    Indexes HTML from a given sitemap URL. The HTML pages are scraped and their data is added to the
    embedding database. This function is specifically designed for the site "https://eak.admin.ch".

    Parameters
    ----------
    sitemap_url : str, optional
        The URL of the sitemap to scrape HTML from. Defaults to "https://eak.admin.ch/eak/de/home.sitemap.xml".
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    db : Session
        Database session

    Returns
    -------
    Response
        Confirmation message upon successful completion of the process.
    """
    docs = await admin_indexer.index(sitemap_url, db, embed=embed)
    return {"message": f"Successfully indexed {len(docs)} PDFs from the {sitemap_url}"}


@app.put("/index_faq_data", summary="Insert Data from faq.bsv.admin.ch", response_description="Insert Data from faq.bsv.admin.ch")
async def index_faq_data(sitemap_url: str = 'https://faq.bsv.admin.ch/sitemap.xml', embed_question: bool = False, embed_answer: bool = False, k: int = 0, db: Session = Depends(get_db)):
    """
    Add and index data for Autocomplete to the FAQ database. The data is obtained by scraping the website `sitemap_url`.

    Parameters
    ==========
    sitemap_url : str, default 'https://faq.bsv.admin.ch/sitemap.xml'
        the `sitemap.xml` URL of the website to scrap
    k : int, default 0
        Number of article to scrap and log to test the method.
    embed_question : bool, default False
        Flag to indicate if the system embeds questions text
    embed_answer : bool, default False
        Flag to indicate if the system embeds answers text
    db : Session, optional
        Database session to use for upserting the extracted

    Returns
    -------
    Response
        Confirmation message upon successful completion of the process
    """
    scraper = BSVIndexer(sitemap_url)
    urls = await scraper.run(k=k, embed=(embed_question, embed_answer), db=db)

    return {"message": f"Done! {len(urls)} wurden verarbeitet."}


@app.put("/data",
         summary="Update or Insert FAQ Data",
         response_model=Question,
         response_description="Updated or Inserted Data")
async def index_data(item: QuestionItem, db: Session = Depends(get_db)):
    """
    Upsert a single entry to the FAQ dataset.

    Parameters
    ----------
    item : QuestionItem
        The Question item to insert or update :
            id : int, optional
                The item if update is wanted
            url : str
                URL where the entry article can be found
            question : str
                The FAQ question
            answer : str
                The question answer
            language : str
                The article language
            source : str
                Username of the user who inserted the data
    db : Session
        Database session

    Returns
    -------
    dict
    """
    logger.info("Upserting data")
    logger.info(item)

    item.source = "username"

    if item.id:
        return question_service.update(db, item)
    else:
        return question_service.create(db, item)
