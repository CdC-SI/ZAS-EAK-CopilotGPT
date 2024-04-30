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

# Function to get embeddings for a text
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002",
    )
    return response['data']

if __name__ == '__main__':

    texts = [
        "I like to eat broccoli and bananas.",
        "I ate a banana and spinach smoothie for breakfast.",
        "Chinchillas and kittens are cute.",
        "My sister adopted a kitten yesterday.",
        "Look at this cute hamster munching on a piece of broccoli.",
    ]

    embeddings = get_embedding(texts)

    connection = create_db_connection()
    if connection is None:
        exit(1)

    cursor = connection.cursor()

    try:
        for text, embedding in zip(texts, embeddings):
            embedding_values = embedding.to_dict()["embedding"]
            cursor.execute(
                "INSERT INTO embeddings (embedding, text, url, created_at, modified_at) VALUES (%s, %s, %s, %s, %s)",
                (embedding_values, text, 'test1.com', '2024-04-24', '2024-04-25')
            )
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        print("Error while writing to DB", error)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()