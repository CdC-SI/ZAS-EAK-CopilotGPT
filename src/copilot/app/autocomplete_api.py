import logging
from typing import List

from autocomplete.autocompleter import autocompleter
from config.base_config import autocomplete_config

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from config.network_config import CORS_ALLOWED_ORIGINS

# Load env variables
from config.base_config import autocomplete_app_config

from sqlalchemy.orm import Session
from database import schemas
from database.service.question import question_service
from database.database import get_db

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create required class instances
app = FastAPI(**autocomplete_app_config)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/",
         summary="Facade for autocomplete",
         response_model=List[schemas.Question],
         response_description="List of matching questions")
async def autocomplete(question: str,
                       language: str = None,
                       k: int = autocomplete_config['results']['limit'],
                       db: Session = Depends(get_db)):
    """
    If combined results of get_exact_match() and get_fuzzy_match() return less than 5 results,
    this method is called after every new "space" character in the question (user query) is
    added as well as when a "?" character is added at the end of the question.

    Parameters
    ----------
    question : str
       User input to match database entries
    language : str, optional
        Question and results language
    k : int, optional
        Number of results to return
    db : Session
        Database session

    Return
    ------
    list of dict
    """
    return await autocompleter.get_autocomplete(db, question, language, k=k)


@app.get("/exact_match",
         summary="Search Questions with exact match",
         response_model=List[schemas.Question],
         response_description="List of matching questions")
def exact_match(question: str,
                language: str = None,
                k: int = autocomplete_config['exact_match']['limit'],
                db: Session = Depends(get_db)):
    """
    Return results from Exact matching

    Parameters
    ----------
    question : str
       User input to match database entries
    language : str, optional
        Question and results language
    k : int, optional
        Number of results to return
    db : Session
        Database session

    Return
    ------
    list of dict
    """
    return question_service.get_exact_match(db, question, language, k=k)


@app.get("/fuzzy_match",
         summary="Search Questions with fuzzy match",
         response_model=List[schemas.Question],
         response_description="List of matching questions")
def fuzzy_match(question: str,
                language: str = None,
                k: int = autocomplete_config['fuzzy_match']['limit'],
                threshold=autocomplete_config['fuzzy_match']['threshold'],
                db: Session = Depends(get_db)):
    """
    Return results from Fuzzy matching

    Parameters
    ----------
    question : str
        User input to match database entries
    language : str, optional
        Question and results language
    k : int, optional
        Number of results to return
    threshold : int, optional
        Levenshtein threshold
    db : Session
        Database session

    Return
    ------
    list of dict
    """
    return question_service.get_fuzzy_match(db, question, threshold=threshold, language=language, k=k)


@app.get("/trigram_match",
         summary="Search Questions with trigram match",
         response_model=List[schemas.Question],
         response_description="List of matching questions")
def trigram_match(question: str,
                  language: str = None,
                  k: int = autocomplete_config['trigram_match']['limit'],
                  threshold=autocomplete_config['trigram_match']['threshold'],
                  db: Session = Depends(get_db)):
    """
    Return results from Trigram matching

    Parameters
    ----------
    question : str
        User input to match database entries
    language : str, optional
        Question and results language
    k : int, optional
        Number of results to return
    db : Session
        Database session

    Return
    ------
    list of dict
    """
    return question_service.get_trigram_match(db, question, threshold=threshold, language=language, k=k)


@app.get("/semantic_similarity_match",
         summary="Search Questions with semantic similarity match",
         response_model=List[schemas.Question],
         response_description="List of matching questions")
def semantic_similarity_match(question: str,
                              language: str = None,
                              k: int = autocomplete_config['semantic_similarity_match']['limit'],
                              db: Session = Depends(get_db)):
    """
    Return results from Semantic Similarity matching

    Parameters
    ----------
    question : str
       User input to match database entries
    language : str, optional
        Question and results language
    k : int, optional
        Number of results to return
    db : Session
        Database session

    Return
    ------
    list of dict
    """
    return question_service.get_semantic_match(db, question, language=language, k=k)
