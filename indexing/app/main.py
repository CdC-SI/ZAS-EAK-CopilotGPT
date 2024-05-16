import logging
from fastapi import FastAPI

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an instance of FastAPI
app = FastAPI()

@app.get("/crawl_data", summary="Crawling endpoint", response_description="Welcome Message")
async def crawl_data():
    """
    Dummy endpoint for data crawling.
    """
    return {"message": "Crawl data test!"}

@app.get("/scrap_data", summary="Scraping Endpoint", response_description="Welcome Message")
async def scrap_data():
    """
    Dummy endpoint for data scraping.
    """
    return {"message": "Scrap data test!"}

@app.get("/index_data", summary="Indexing Endpoint", response_description="Welcome Message")
async def index_data():
    """
    Dummy endpoint for data indexing.
    """
    return {"message": "Index data test!"}

@app.get("/parse_faq_data", summary="FAQ Parsing Endpoint", response_description="Welcome Message")
async def parse_faq_data():
    """
    Dummy endpoint for FAQ data parsing.
    """
    return {"message": "Parsing FAQ data test!"}

@app.get("/parse_rag_data", summary="Parsing Endpoint", response_description="Welcome Message")
async def parse_rag_data():
    """
    Dummy endpoint for data parsing (RAG).
    """
    return {"message": "Parsing RAG data test!"}

@app.get("/chunk_rag_data", summary="Chunking Endpoint", response_description="Welcome Message")
async def chunk_rag_data():
    """
    Dummy endpoint for data chunking (RAG).
    """
    return {"message": "Chunking data test!"}