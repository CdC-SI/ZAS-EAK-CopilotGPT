import logging

from autocompleter import *

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# Load env variables
from config.base_config import autocomplete_app_config
from config.network_config import CORS_ALLOWED_ORIGINS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create required class instances
app = FastAPI(**autocomplete_app_config)
autocompleter = Autocompleter()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/autocomplete/",
         summary="Facade for autocomplete",
         response_description="List of matching questions")
async def autocomplete(question: str, language: str = '*'):
    """
     If combined results of get_exact_match() and get_fuzzy_match() return less than 5 results,
     this method is called after every new "space" character in the question (user query) is
     added as well as when a "?" character is added at the end of the question.
    """
    return autocompleter.get_autocomplete(question, language)


@app.get("/autocomplete/exact_match/",
         summary="Search Questions with exact match",
         response_description="List of matching questions")
async def exact_match(question: str, language: str = '*'):
    return autocompleter.get_exact_match(question, language)


@app.get("/autocomplete/fuzzy_match/",
         summary="Search Questions with fuzzy match",
         response_description="List of matching questions")
async def fuzzy_match(question: str, language: str = '*'):
    return autocompleter.get_fuzzy_match(question, language)


@app.get("/autocomplete/semantic_similarity_match/",
         summary="Search Questions with semantic similarity match",
         response_description="List of matching questions")
async def semantic_similarity_match(question: str, language: str = '*'):
    return autocompleter.get_semantic_similarity_match(question, language)
