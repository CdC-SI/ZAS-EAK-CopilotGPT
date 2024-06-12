import logging

from typing import Union

from autocomplete.app.autocompleter import *

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Load env variables
from config.base_config import autocomplete_app_config
from config.network_config import CORS_ALLOWED_ORIGINS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

_autocompleter: Union[Autocompleter, None] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _autocompleter
    _autocompleter = Autocompleter()
    yield


# Create required class instances
app = FastAPI(**autocomplete_app_config, lifespan=lifespan)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/autocomplete/",
         summary="Facade for autocomplete",
         response_description="List of matching questions")
async def autocomplete(question: str, language: str = '*'):
    """
     If combined results of get_exact_match() and get_fuzzy_match() return less than 5 results,
     this method is called after every new "space" character in the question (user query) is
     added as well as when a "?" character is added at the end of the question.
    """
    return await _autocompleter.get_autocomplete(question, language)


@app.get("/autocomplete/exact_match/",
         summary="Search Questions with exact match",
         response_description="List of matching questions")
async def exact_match(question: str, language: str = '*'):
    return await _autocompleter.get_exact_match(question, language)


@app.get("/autocomplete/fuzzy_match/",
         summary="Search Questions with fuzzy match",
         response_description="List of matching questions")
async def fuzzy_match(question: str, language: str = '*'):
    return await _autocompleter.get_fuzzy_match(question, language)


@app.get("/autocomplete/semantic_similarity_match/",
         summary="Search Questions with semantic similarity match",
         response_description="List of matching questions")
async def semantic_similarity_match(question: str, language: str = '*'):
    return await _autocompleter.get_semantic_similarity_match(question, language)
