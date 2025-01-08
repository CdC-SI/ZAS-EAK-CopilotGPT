import logging
import os
from typing import List

from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

from pathlib import Path

# Load env variables
from config.base_config import indexing_config, indexing_app_config

# Load utility functions
from indexing.pipelines.admin import admin_indexer
from indexing.pipelines.ahv import ahv_indexer
from indexing.pipelines.bsv import BSVIndexer

from sqlalchemy.orm import Session
from database.service.question import question_service
from database.service.document import document_service
from database.service.tag import tag_service
from schemas.question import Question, QuestionCreate, QuestionItem
from schemas.document import DocumentCreate
from schemas.tag import TagCreate
from database.database import get_db

# Load models
from schemas.indexing import ResponseBody

import tempfile
import shutil
import ast
import csv
import codecs

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def init_indexing():
    """
    Initialize the database according to the configuration ``indexing_config`` specified in ``config.yaml``
    """
    if indexing_config["faq"]["auto_index"]:
        # With dev-mode, only index sample FAQ data
        if indexing_config["dev_mode"]:
            try:
                logger.info("Auto-indexing sample FAQ data")
                add_faq_data_from_csv()
            except Exception as e:
                logger.error(
                    "Dev-mode: Failed to index sample FAQ data: %s", e
                )
        # If dev-mode is deactivated, scrap and index all bsv.admin.ch FAQ data
        else:
            try:
                logger.info("Auto-indexing bsv.admin.ch FAQ data")
                await index_faq_data()
            except Exception as e:
                logger.error("Failed to index bsv.admin.ch FAQ data: %s", e)

    if indexing_config["rag"]["auto_index"]:
        # With dev-mode, only index sample data
        if indexing_config["dev_mode"]:
            try:
                logger.info("Auto-indexing sample RAG data")
                add_rag_data_from_csv()
            except Exception as e:
                logger.error("Failed to index sample RAG data: %s", e)
        # If dev-mode is deactivated, scrap and index all RAG data (NOTE: Will be implemented soon.)
        else:
            raise NotImplementedError("Feature is not implemented yet.")


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


@app.post(
    "/upload_csv_rag",
    summary="Upload a CSV file for RAG data",
    status_code=200,
    response_model=ResponseBody,
)
async def upload_csv_rag(
    file: UploadFile = File(...),
    embed: bool = False,
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file containing RAG data to the database with optional embeddings.
    The function acknowledges the following columns:

    - *url:* source URL of the document
    - *text:* Text content of the document
    - *language (optional):* Language of the document
    - *embedding (optional):* Embedding of the document
    - *tags (optional):* Tags of the document

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
    ResponseBody
        A response body containing a confirmation message upon successful completion of the process.
    """
    logger.info(f"Downloading {file.filename}...")
    data = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))

    embedding_column = "embedding" in data.fieldnames
    language_column = "language" in data.fieldnames
    tags_column = "tags" in data.fieldnames
    organization_column = "organization" in data.fieldnames

    logger.info("Start adding data to database...")
    i = 0
    for row in data:
        embedding = (
            ast.literal_eval(row["embedding"]) if embedding_column else None
        )
        language = row["language"] if language_column else None
        tags = (
            [tag.strip() for tag in row["tags"].split(",")]
            if tags_column and row["tags"]
            else None
        )
        organization = (
            row["organization"]
            if organization_column and row["organization"]
            else None
        )
        document = DocumentCreate(
            url=row["url"],
            text=row["text"],
            embedding=embedding,
            source=file.filename,
            language=language,
            tags=tags,
            organization=organization,
        )
        await document_service.upsert(db, document, embed=embed)
        i += 1

    file.file.close()
    logger.info(f"Finished adding {i} entries to RAG database.")
    return {"content": f"Successfully added {i} entries to RAG database."}


@app.post(
    "/upload_csv_faq",
    summary="Upload a CSV file for FAQ data",
    status_code=200,
    response_model=ResponseBody,
)
async def upload_csv_faq(
    file: UploadFile = File(...),
    embed: bool = False,
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file containing RAG data to the database with optional embeddings.
    The function acknowledges the following columns:

    - *url:* source URL of the information
    - *text:* Text content of the question
    - *answer:* Text content of the answer
    - *language (optional):* Language of the question and answer
    - *embedding (optional):* Embedding of the question
    - *tags (optional):* Tags of the document

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
    ResponseBody
        A response body containing a confirmation message upon successful completion of the process.
    """
    logger.info(f"Downloading {file.filename}...")
    data = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))

    embedding_column = "embedding" in data.fieldnames
    language_column = "language" in data.fieldnames
    tags_column = "tags" in data.fieldnames

    logger.info("Start adding data to database...")
    i = 0
    for row in data:
        embedding = (
            ast.literal_eval(row["embedding"]) if embedding_column else None
        )
        language = row["language"] if language_column else None
        tags = row["tags"] if tags_column else None

        question = QuestionCreate(
            url=row["url"],
            text=row["text"],
            answer=row["answer"],
            embedding=embedding,
            source=file.filename,
            language=language,
            tags=tags,
        )
        await question_service.upsert(db, question, embed=embed)
        i += 1

    file.file.close()
    logger.info(f"Finished adding {len(list(data))} entries to FAQ database.")
    return {"content": f"Successfully added {i} entries to FAQ database."}


@app.post(
    "/upload_csv_tags",
    summary="Upload a CSV file for tags data",
    status_code=200,
    response_model=ResponseBody,
)
async def upload_csv_tags(
    file: UploadFile = File(...),
    embed: bool = False,
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file containing tags data to the database with optional embeddings.
    The function acknowledges the following columns:

    - *tags_en:* Tag name in english
    - *description_en:* English description of the tag
    - *description:* Description of the tag
    - *language:* Language of the tag
    - *embedding (optional):* Embedding of the description

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
    ResponseBody
        A response body containing a confirmation message upon successful completion of the process.
    """
    logger.info(f"Downloading {file.filename}...")
    data = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))

    embedding_column = "embedding" in data.fieldnames
    language_column = "language" in data.fieldnames
    tag_en_column = "tag_en" in data.fieldnames
    description_en_column = "description_en" in data.fieldnames
    description_column = "description" in data.fieldnames

    logger.info("Start adding data to database...")
    i = 0
    for row in data:
        embedding = (
            ast.literal_eval(row["embedding"]) if embedding_column else None
        )
        language = row["language"] if language_column else None
        tag_en = (
            row["tag_en"].strip() if tag_en_column and row["tag_en"] else None
        )
        description_en = (
            row["description_en"].strip()
            if description_en_column and row["description_en"]
            else None
        )
        description = (
            row["description"].strip()
            if description_column and row["description"]
            else None
        )

        tag = TagCreate(
            tag_en=tag_en,
            description_en=description_en,
            description=description,
            language=language,
            embedding=embedding,
        )
        await tag_service.upsert(db, tag, embed=embed)
        i += 1

    file.file.close()
    logger.info(f"Finished adding {i} entries to tags database.")
    return {"content": f"Successfully added {i} entries to tags database."}


@app.post(
    "/upload_pdf_rag",
    summary="Upload a PDF files for RAG data",
    status_code=200,
    response_model=ResponseBody,
)
async def upload_pdf_rag(
    files: List[UploadFile] = File(..., description="PDF files only"),
    embed: bool = False,
    user_uuid: str = None,
    language: str = "de",
    db: Session = Depends(get_db),
):
    """
    Upload a CSV file containing RAG data to the database.

    Parameters
    ----------
    files : List[UploadFile]
        The PDF file sent by the user
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    user_uuid : str, optional
        UUID of the user who uploaded the file
    db : Session
        Database session

    Returns
    -------
    ResponseBody
        A response body containing a confirmation message upon successful completion of the process.
    """
    logger.info("Starting PDF upload")
    uploaded_files = []
    for file in files:
        logger.info(f"Processing file: {file.filename}")
        if file.content_type != "application/pdf":
            logger.error(f"{file.filename} is not a valid PDF file.")
            return {"content": f"{file.filename} is not a valid PDF file."}

        # Handle temporary file creation and processing
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".pdf"
        ) as temp_file:
            temp_filename = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        # Index data in vectorDB
        await ahv_indexer.add_content_to_db(
            db,
            content=[Path(temp_filename)],
            source=file.filename,
            user_uuid=user_uuid,
            language=language,
            embed=embed,
        )
        uploaded_files.append(file.filename)
        logger.info(f"File {file.filename} processed successfully")

        os.remove(temp_filename)  # Clean up temp file after use

    logger.info(f"Finished uploading {len(uploaded_files)} files")
    return {
        "content": f"{len(uploaded_files)} files indexed successfully",
        "files": uploaded_files,
    }


@app.post(
    "/add_rag_data_from_csv",
    summary="Insert data for RAG without embedding from a local csv file",
    status_code=200,
    response_model=ResponseBody,
)
def add_rag_data_from_csv(
    file_path: str = "indexing/data/rag_test_data.csv",
    embed: bool = False,
    db: Session = Depends(get_db),
):
    """
    Add and index test data for RAG from csv files with optional embeddings.
    The function acknowledges the following columns:

    - *url:* source URL of the document
    - *text:* Text content of the document
    - *language (optional):* Language of the document
    - *embedding (optional):* Embedding of the document
    - *tags (optional):* Tags of the document

    Parameters
    ----------
    file_path : str, optional
        Path to the csv file containing the data. Defaults to "indexing/data/rag_test_data.csv".
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    db : Session
        Database session

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    with open(file_path, mode="r") as file:
        data = csv.DictReader(file)

        embedding_column = "embedding" in data.fieldnames
        language_column = "language" in data.fieldnames
        tags_column = "tags" in data.fieldnames
        organization_column = "organization" in data.fieldnames

        i = 0
        for row in data:
            embedding = (
                ast.literal_eval(row["embedding"])
                if embedding_column
                else None
            )
            language = row["language"] if language_column else None
            tags = (
                [tag.strip() for tag in row["tags"].split(",")]
                if tags_column and row["tags"]
                else None
            )
            organization = row["organization"] if organization_column else None

            document = DocumentCreate(
                url=row["url"],
                text=row["text"],
                embedding=embedding,
                source=file_path,
                language=language,
                tags=tags,
                organization=organization,
            )
            document_service.upsert(db, document, embed=embed)
            i += 1

    logger.info(f"Finished adding {i} entries to RAG database.")
    return {"content": f"Successfully added {i} entries to RAG database."}


@app.post(
    "/add_faq_data_from_csv",
    summary="Insert data for FAQ without embedding from a local csv file",
    status_code=200,
    response_model=ResponseBody,
)
def add_faq_data_from_csv(
    file_path: str = "indexing/data/faq_test_data.csv",
    embed: bool = False,
    db: Session = Depends(get_db),
):
    """
    Add and index test data for RAG from csv files with optional embeddings.
    The function acknowledges the following columns:

    - *url:* source URL of the information
    - *text:* Text content of the question
    - *answer:* Text content of the answer
    - *language (optional):* Language of the question and answer
    - *embedding (optional):* Embedding of the question
    - *tags (optional):* Tags of the document

    Parameters
    ----------
    file_path : str, optional
        Path to the csv file containing the data. Defaults to "indexing/data/faq_test_data.csv".
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    db : Session
        Database session

    Returns
    -------
    str
        Confirmation message upon successful completion of the process
    """
    with open(file_path, mode="r") as file:
        data = csv.DictReader(file)

        embedding_column = "embedding" in data.fieldnames
        language_column = "language" in data.fieldnames
        tags_column = "tags" in data.fieldnames

        for row in data:
            embedding = (
                ast.literal_eval(row["embedding"])
                if embedding_column
                else None
            )
            language = row["language"] if language_column else None
            tags = row["tags"] if tags_column else None

            question = QuestionCreate(
                url=row["url"],
                text=row["text"],
                answer=row["answer"],
                embedding=embedding,
                source=file_path,
                language=language,
                tags=tags,
            )
            question_service.upsert(db, question, embed=embed)

    logger.info("Finished adding entries to FAQ database.")
    return {"content": "Successfully added entries to FAQ database."}


@app.post(
    "/embed_rag_data",
    summary="Embed all data for RAG that have not been embedded yet",
    status_code=200,
    response_model=ResponseBody,
)
def embed_rag_data(
    db: Session = Depends(get_db), embed_empty_only: bool = True, k: int = 0
):
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
    str
        Confirmation message upon successful completion of the process
    """
    document_service.embed_many(db, embed_empty_only, k)
    return {"content": "yay"}


@app.post(
    "/embed_faq_data",
    summary="Embed all data for FAQ that have not been embedded yet",
    status_code=200,
    response_model=ResponseBody,
)
def embed_faq_data(
    db: Session = Depends(get_db), embed_empty_only: bool = True, k: int = 0
):
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
    str
        Confirmation message upon successful completion of the process
    """
    question_service.embed_many(db, embed_empty_only, k)
    return {"content": "yay"}


@app.post(
    "/index_pdfs_from_sitemap",
    summary="Index memento PDFs from the https://www.ahv-iv.ch/de/Sitemap-DE sitemap",
    response_description="Confirmation message upon successful indexing",
    status_code=200,
    response_model=ResponseBody,
)
async def index_pdfs_from_sitemap(
    sitemap_url: str = "https://www.ahv-iv.ch/de/Sitemap-DE",
    embed: bool = False,
    db: Session = Depends(get_db),
):
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
    ResponseBody
        A response body containing a confirmation message upon successful completion of the process.
    """
    return await ahv_indexer.index(sitemap_url, db, embed=embed)


@app.post(
    "/index_html_from_sitemap",
    summary="Index HTML from a sitemap",
    response_description="Confirmation message upon successful indexing",
    status_code=200,
    response_model=ResponseBody,
)
async def index_html_from_sitemap(
    sitemap_url: str = "https://eak.admin.ch/eak/de/home.sitemap.xml",
    embed: bool = False,
    db: Session = Depends(get_db),
):
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
    ResponseBody
        A response body containing a confirmation message upon successful completion of the process.
    """
    return await admin_indexer.index(sitemap_url, db, embed=embed)


@app.put(
    "/index_faq_data",
    summary="Insert Data from faq.bsv.admin.ch",
    response_description="Insert Data from faq.bsv.admin.ch",
)
async def index_faq_data(
    sitemap_url: str = "https://faq.bsv.admin.ch/sitemap.xml",
    embed_question: bool = False,
    embed_answer: bool = False,
    k: int = 0,
    db: Session = Depends(get_db),
):
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
    str
        Confirmation message upon successful completion of the process
    """
    logging.basicConfig(level=logging.INFO)

    scraper = BSVIndexer(sitemap_url)
    urls = await scraper.run(k=k, embed=(embed_question, embed_answer), db=db)

    return {"message": f"Done! {len(urls)} wurden verarbeitet."}


@app.put(
    "/data",
    summary="Update or Insert FAQ Data",
    response_model=Question,
    response_description="Updated or Inserted Data",
)
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

    item.source = "placeholder_user"

    if item.id:
        db_question = question_service.get(db, item.id)
        return await question_service.update(db, db_question, item)
    else:
        return await question_service.create(db, item)
