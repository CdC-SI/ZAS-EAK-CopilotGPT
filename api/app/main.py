import os
from dotenv import load_dotenv

import asyncpg
import logging
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from web_scraper import WebScraper

# Create an instance of FastAPI
app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_db_connection():
    """Establish a database connection."""
    conn = await asyncpg.connect(**DB_PARAMS)
    return conn


@app.get("/", summary="Root Endpoint", response_description="Welcome Message")
async def read_root():
    """
    Root endpoint.

    Returns a welcome message indicating that FastAPI is running.
    """
    return {"message": "Hello, FastAPI!"}


@app.get("/search/", summary="Search Questions", response_description="List of matching questions")
async def search_questions(question: str):
    """
    Search for questions that contain the specified string, case-insensitive.

    - **question**: string to be searched within the questions.

    Returns a list of questions that match the search criteria. If no matches are found, returns a 404 error.
    """
    conn = await get_db_connection()
    try:
        # Convert both the 'question' column and the search string to lowercase to perform a case-insensitive search
        search_query = f"%{question.lower()}%"
        rows = await conn.fetch("SELECT * FROM data WHERE LOWER(question) LIKE $1", search_query)
        await conn.close()  # Close the database connection

        if not rows:
            raise HTTPException(status_code=404, detail="Question not found")

        # Convert the results to a list of dictionaries
        questions = [dict(row) for row in rows]
        return questions
    except Exception as e:
        await conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/data/", summary="Update or Insert Data", response_description="Updated or Inserted Data")
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
                raise HTTPException(status_code=500, detail=f"Update exception: {str(e)}")
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
                raise HTTPException(status_code=500, detail=f"Insert exception: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@app.put("/init_expert", summary="Insert Data from faq.bsv.admin.ch", response_description="Insert Data from faq.bsv.admin.ch")
async def ignite_expert():
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

if __name__ == "__main__":

    # Load environment variables
    load_dotenv()
    CORS_ALLOWED_ORIGINS = os.environ["CORS_ALLOWED_ORIGINS"]
    POSTGRES_USER = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    POSTGRES_DB = os.environ["POSTGRES_DB"]
    POSTGRES_HOST = "db"

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[CORS_ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Database connection parameters
    DB_PARAMS = {
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "database": POSTGRES_DB,
        "host": POSTGRES_HOST,
    }