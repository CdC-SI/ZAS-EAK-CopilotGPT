import logging
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware

from autocomplete.app.web_scraper import WebScraper
from autocompleter import *

# Load env variables
from config import CORS_ALLOWED_ORIGINS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an instance of FastAPI
app = FastAPI()
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


@app.get("/autocomplete/", summary="Facade for autocomplete", response_description="List of matching questions")
async def autocomplete(question: str, language: str = '*'):
    """
     If combined results of get_exact_match() and get_fuzzy_match() return less than 5 results, this method is called after every new "space" character in the question (user query) is added as well as when a "?" character is added at the end of the question.
    """
    return autocompleter.get_autocomplete(question, language)


@app.get("/autocomplete/exact_match/", summary="Search Questions with exact match", response_description="List of matching questions")
async def exact_match(question: str, language: str = '*'):
    return autocompleter.get_exact_match(question, language)


@app.get("/autocomplete/fuzzy_match/", summary="Search Questions with fuzzy match", response_description="List of matching questions")
async def fuzzy_match(question: str, language: str = '*'):
    return autocompleter.get_fuzzy_match(question, language)


@app.get("/autocomplete/semantic_similarity_match/", summary="Search Questions with semantic similarity match", response_description="List of matching questions")
async def semantic_similarity_match(question: str, language: str = '*'):
    return autocompleter.get_semantic_similarity_match(question, language)


@app.put("/autocomplete/data/", summary="Update or Insert Data", response_description="Updated or Inserted Data")
async def update_or_insert_data(
    url: str,
    question: str,
    answer: str,
    language: str,
    id: int = Body(None)
):
    """
    Update an existing data record or insert a new one based on the presence of the question.

    - **url**: The URL associated with the data.
    - **question**: The question.
    - **answer**: The answer.
    - **language**: The language of the data.

    Returns the updated or inserted data record.

    Note: The operation now checks for the presence of a question in the database to decide between insert and update.
    """
    conn = await get_db_connection()
    try:
        # Convert the search question to lowercase to perform a case-insensitive search
        search_query = f"%{question.lower()}%"
        # Check if a record with the same question exists
        existing_row = await conn.fetchrow("SELECT * FROM data WHERE LOWER(question) LIKE $1", search_query)

        if existing_row:
            # Update the existing record
            try:
                await conn.execute(
                    "UPDATE data SET url = $1, question = $2, answer = $3, language = $4 WHERE id = $5",
                    url, question, answer, language, existing_row['id']
                )
                logger.info(f"Update: {url}")
                return {"id": existing_row['id'], "url": url, "question": question, "answer": answer, "language": language}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Update exception: {str(e)}") from e
        else:
            # Insert a new record
            try:
                row = await conn.fetchrow(
                    "INSERT INTO data (url, question, answer, language) VALUES ($1, $2, $3, $4) RETURNING id",
                    url, question, answer, language
                )
                logger.info(f"Insert: {url}")
                return {"id": row['id'], "url": url, "question": question, "answer": answer, "language": language}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Insert exception: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        await conn.close()

@app.put("/autocomplete/init_expert/", summary="Insert Data from faq.bsv.admin.ch", response_description="Insert Data from faq.bsv.admin.ch")
async def init_expert():
    """
    Asynchronously retrieves and processes FAQ data from 'https://faq.bsv.admin.ch' to insert into the database.

    The endpoint 'https://faq.bsv.admin.ch/sitemap.xml' is utilized to discover all relevant FAQ URLs. For each URL,
    the method extracts the primary question (denoted by the 'h1' tag) and its corresponding answer (within an 'article' tag).
    Unnecessary boilerplate text will be removed for clarity and conciseness.

    Each extracted FAQ entry is then upserted (inserted or updated if already exists) into the database, with detailed
    logging to track the operation's progress and identify any errors.

    Returns a confirmation message upon successful completion of the process.

    TODO:
    - Consider implementing error handling at a more granular level to retry failed insertions or updates, enhancing the robustness of the data ingestion process.
    - Explore optimization opportunities in text extraction and processing to improve efficiency and reduce runtime, especially for large sitemaps.
    """
    logging.basicConfig(level=logging.INFO)

    sitemap_url = 'https://faq.bsv.admin.ch/sitemap.xml'
    scraper = WebScraper(sitemap_url)

    scraper.logger.info(f"Beginne Datenextraktion für: {sitemap_url}")
    urls = scraper.get_sitemap_urls()

    for url in urls:
        extracted_h1 = scraper.extract_text_from_tag(url, 'h1')
        extracted_article = scraper.extract_text_from_tag(url, 'article')
        language = scraper.detect_language(url)

        # Efficient text processing
        for term in ['Antwort\n', 'Rispondi\n', 'Réponse\n']:
            extracted_article = extracted_article.replace(term, '')

        if extracted_h1 and extracted_article:
            try:
                logger.info(f"extract: {url}")
                await update_or_insert_data(
                    url=url,
                    question=extracted_h1,
                    answer=extracted_article,
                    language=language,
                    id=None
                )
            except Exception as e:
                logger.error(f"Error: {e}")

    logger.info(f"Done! {len(urls)} wurden verarbeitet.")
    return {"message": f"Done! {len(urls)} wurden verarbeitet."}
