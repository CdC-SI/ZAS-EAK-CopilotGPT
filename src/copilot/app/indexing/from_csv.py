import os

from config.config import IndexingConfig

from sqlalchemy.orm import Session
from database.database import SessionLocal
from fastapi import UploadFile

from database.service.question import question_service
from database.service.document import document_service
from schemas.document import DocumentCreate
from schemas.question import QuestionCreate

from enum import Enum
import ast
import codecs
import csv

from utils.logging import get_logger
logger = get_logger(__name__)


class CreateService(Enum):
    FAQ = (QuestionCreate, question_service)
    RAG = (DocumentCreate, document_service)


def init_indexing():
    """
    Initialize the database according to the configuration ``indexing_config`` specified in ``config.yaml``
    """
    if IndexingConfig.auto_init:
        db: Session = SessionLocal()
        try:
            for create_service in CreateService:
                for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), 'data', create_service.name)):
                    for file in files:
                        if file.endswith(".csv"):
                            filepath = os.path.join(root, file)

                            logger.info(f"Auto-indexing {create_service.name} data from csv file {filepath}")
                            add_data_from_local(filepath, db, create_service)
        finally:
            db.close()


def add_data(data: csv.DictReader, create_service: CreateService, db: Session, source: str, embed: bool = False):
    to_update = ['embedding']  # Columns that need to be updated
    col_update = [col for col in to_update if col in data.fieldnames]  # Check if the columns exist in the data
    create, service = create_service.value

    logger.info(f'Start adding data to the {create_service.name} database...')
    i = 0
    for row in data:
        row.update({col: ast.literal_eval(row[col]) for col in col_update})  # Format the columns that need to
        document = create(**row, source=source)
        service.upsert(db, document, embed=embed)
        i += 1

    logger.info(f'Finished adding {i} entries to the {create_service.name} database.')
    return i


def add_data_from_local(file_path: str, db: Session, create_service: CreateService, embed: bool = False):
    """
    Add and index test data for RAG from a local csv files with optional embeddings.
    Please refer to the pydantic models `DocumentCreate` or `QuestionCreate` for the expected fields.

    Parameters
    ----------
    file_path : str, optional
        Path to the csv file containing the data.
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    create_service : CreateService
        The service to use for creating the data
    db : Session
        Database session
    """
    with open(file_path, mode='r') as file:
        data = csv.DictReader(file)
        add_data(data, create_service, db, file_path, embed)


def add_data_from_upload(file: UploadFile, db: Session, create_service: CreateService, embed: bool = False):
    """
    Add and index test data for RAG from an uploaded csv file with optional embeddings.
    Please refer to the pydantic models `DocumentCreate` or `QuestionCreate` for the expected fields.

    Parameters
    ----------
    file : File
        The csv file containing the data.
    embed : bool, optional
        Whether to embed the data or not. Defaults to False.
    create_service : CreateService
        The service to use for creating the data
    db : Session
        Database session
    """
    logger.info(f'Downloading {file.filename}...')
    try:
        data = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))

        n_entries = add_data(data, create_service, db, file.filename, embed)
    finally:
        file.file.close()

    return n_entries
