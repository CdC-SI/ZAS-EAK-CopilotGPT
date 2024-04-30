from dotenv import load_dotenv
import os
import psycopg2
import openai

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

# Database connection parameters
DB_PARAMS = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "database": POSTGRES_DB,
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
}

def create_db_connection():
    """Establish a database connection."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to the database: {e}")
        return None

def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002",
    )
    return response['data']

if __name__ == '__main__':

    text = "Qu'est-ce qui change avec AVS 21?"
    embedding = get_embedding(text)[0]["embedding"]

    connection = create_db_connection()
    if connection is None:
        exit(1)

    cursor = connection.cursor()

    try:
        cursor.execute(f"""
            SELECT text,  1 - (embedding <=> '{embedding}') AS cosine_similarity
            FROM embeddings
            ORDER BY cosine_similarity desc
            LIMIT 1
        """)
        for r in cursor.fetchall():
            print(f"Text: {r[0]}; Similarity: {r[1]}")
    except Exception as error:
        print("Error: ", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()