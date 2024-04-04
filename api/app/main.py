import asyncpg
import logging
from fastapi import FastAPI, HTTPException, Body
from index_pipeline import get_sitemap_urls, extract_text_from_url


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an instance of FastAPI
app = FastAPI()

# Database connection parameters
DB_PARAMS = {
    "user": "admin",
    "password": "password",
    "database": "chuck_norris",
    "host": "db"
}

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
    id: int = Body(None)
):
    """
    Update an existing data record or insert a new one.

    - **url**: The URL associated with the data.
    - **question**: The question.
    - **answer**: The answer.
    - **id**: The ID of the data record to update (optional).

    Returns the updated or inserted data record.

    TODO:
    - important: The upsert operation is currently not working because it is implemented by id, and not by url.
    """
    conn = await get_db_connection()
    try:
        if id:
            # Update an existing record
            await conn.execute(
                "UPDATE data SET url = $1, question = $2, answer = $3 WHERE id = $4",
                url, question, answer, id
            )
            return {"id": id, "url": url, "question": question, "answer": answer}
        else:
            # Insert a new record
            row = await conn.fetchrow(
                "INSERT INTO data (url, question, answer) VALUES ($1, $2, $3) RETURNING id",
                url, question, answer
            )
            return {"id": row["id"], "url": url, "question": question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@app.put("/ignite_expert", summary="Insert Data from faq.bsv.admin.ch", response_description="Insert Data from faq.bsv.admin.ch")
async def ignite_expert():
    """
    Asynchronously retrieves and processes FAQ data from 'https://faq.bsv.admin.ch' to insert into the database.
    
    The endpoint 'https://faq.bsv.admin.ch/sitemap.xml' is utilized to discover all relevant FAQ URLs. For each URL, 
    the method extracts the primary question (denoted by the 'h1' tag) and its corresponding answer (within an 'article' tag). 
    Unnecessary boilerplate text such as 'Antwort\n', 'Rispondi\n', and 'Réponse\n' is removed for clarity and conciseness.
    
    Each extracted FAQ entry is then upserted (inserted or updated if already exists) into the database, with detailed 
    logging to track the operation's progress and identify any errors. 
    
    Returns a confirmation message upon successful completion of the process.
    
    TODO:
    - important: The upsert operation is currently not working because it is implemented by id, and not by url.
    - Consider implementing error handling at a more granular level to retry failed insertions or updates, enhancing the robustness of the data ingestion process.
    - Explore optimization opportunities in text extraction and processing to improve efficiency and reduce runtime, especially for large sitemaps.
    - Evaluate the possibility of adding multi-language support to cater to all variations of FAQs provided in different languages.
    """
    
    sitemap_url = 'https://faq.bsv.admin.ch/sitemap.xml'
    urls = get_sitemap_urls(sitemap_url)
    
    for url in urls:
        extracted_h1 = extract_text_from_url(url, 'h1')
        extracted_article = extract_text_from_url(url, 'article')
        
        # Efficient text processing
        for term in ['Antwort\n', 'Rispondi\n', 'Réponse\n']:
            extracted_article = extracted_article.replace(term, '')
        
        if extracted_h1:
            try:
                logger.info(f"extract: {url}")
                await update_or_insert_data(
                    url=url,
                    question=extracted_h1,
                    answer=extracted_article,
                    id=None
                )
            except Exception as e:
                logger.error(f"Error: {e}")
    logger.info("Done")
    return {"message": "Done"}
