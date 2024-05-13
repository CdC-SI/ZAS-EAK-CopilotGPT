import os
from dotenv import load_dotenv

import psycopg2
import openai
from datetime import datetime

import logging
from fastapi import FastAPI, HTTPException

from models import ResponseBody, RAGRequest

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an instance of FastAPI
app = FastAPI()

# Load env variables
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PORT = os.environ["POSTGRES_PORT"]

# Database connection parameters
DB_PARAMS = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "database": POSTGRES_DB,
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
}

# Function to create a db connection
def create_db_connection():
    """Establish a database connection."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail="Database connection failed") from e

# Function to get embeddings for a text
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002",
    )

    return response['data']

@app.post("/init_embeddings/", summary="Insert Embedding data for RAG", response_description="Insert Embedding data for RAG", status_code=200, response_model=ResponseBody)
async def init_embeddings():

    texts = [
        ("Comment déterminer mon droit aux prestations complémentaires? Vous pouvez déterminer votre droit aux prestations de façon simple et rapide, grâce au calculateur de prestations complémentaires en ligne : www.ahv-iv.ch/r/calculateurpc\n\n Le calcul est effectué de façon tout à fait anonyme. Vos données ne sont pas enregistrées. Le résultat qui en ressort constitue une estimation provisoire fondée sur une méthode de calcul simplifiée. Il s’agit d’une estimation sans engagement, qui ne tient pas lieu de demande de prestation et n’implique aucun droit. Le calcul n’est valable que pour les personnes qui vivent à domicile. Si vous résidez dans un home, veuillez vous adresser à sa direction, qui vous fournira les renseignements appropriés au sujet des prestations complémentaires.", "https://www.ahv-iv.ch/p/5.02.f"),
        ("Quand des prestations complémentaires sont-elles versées ? Lorsque la rente AVS ne suffit pas. Les rentes AVS sont en principe destinées à couvrir les besoins vitaux d'un assuré. Lorsque ces ressources ne sont pas suffisantes pour assurer la subsistance des bénéficiaires de rentes AVS, ceux-ci peuvent prétendre à des prestations complémentaires (PC).\n\nLe versement d'une telle prestation dépend du revenu et de la fortune de chaque assuré. Les PC ne sont pas des prestations d'assistance mais constituent un droit que la personne assurée peut faire valoir en toute légitimité lorsque les conditions légales sont réunies.", "https://www.ahv-iv.ch/fr/Assurances-sociales/Assurance-vieillesse-et-survivants-AVS/Prestations-compl%C3%A9mentaires"),
        ("Quand le droit à une rente de vieillesse prend-il naissance ? Lorsque la personne assurée atteint l'âge de référence. Le droit à la rente de vieillesse prend naissance le premier jour du mois qui suit celui au cours duquel l'ayant droit atteint l'âge ordinaire de référence et s'éteint à la fin du mois de son décès. L'âge ordinaire de la retraite est fixé à 64 ans pour les femmes et à 65 ans pour les hommes. A partir du 1er janvier 2025, l'âge est fixé à 65 ans pour les hommes, tandis que pour les femmes, il est actuellement fixé à 64 ans et sera relevé de trois mois par an. À partir de 2028, l’âge de référence sera le même, à savoir 65 ans, pour les hommes et les femmes.", "https://www.ahv-iv.ch/fr/Assurances-sociales/Assurance-vieillesse-et-survivants-AVS/Rentes-de-vieillesse#qa-792"),
        ("Qu'est-ce qui change avec AVS 21? Le 25 septembre 2022, le peuple et les cantons ont accepté la réforme AVS 21 et assuré ainsi un financement suffisant de l’AVS jusqu’à l’horizon 2030. La modification entrera en vigueur le 1er janvier 2024. La réforme comprenait deux objets : la modification de la loi sur l’assurance-vieillesse et survivants (LAVS) et l’arrêté fédéral sur le financement additionnel de l’AVS par le biais d’un relèvement de la TVA. Les deux objets étaient liés. Ainsi, le financement de l’AVS et le niveau des rentes seront garantis pour les prochaines années. L’âge de référence des femmes sera relevé à 65 ans, comme pour les hommes, le départ à la retraite sera flexibilisé et la TVA augmentera légèrement. La stabilisation de l’AVS comprend quatre mesures : \n\n• harmonisation de l’âge de la retraite (à l’avenir «âge de référence») des femmes et des hommes à 65 ans\n• mesures de compensation pour les femmes de la génération transitoire\n• retraite flexible dans l’AVS\n• financement additionnel par le relèvement de la TVA", "https://www.ahv-iv.ch/p/31.f"),
        ("Que signifie l'âge de la retraite flexible ? La rente peut être anticipée ou ajournée. Anticipation de la rente : Femmes et hommes peuvent anticiper la perception de leur rente dès le premier jour du mois qui suit leur 63e anniversaire. Les femmes nées entre 1961 et 1969 pourront continuer à anticiper leur rente à 62 ans. Leur situation est régie par des dispositions transitoires spéciales. Pour plus d’informations à ce sujet, veuillez vous adresser à votre caisse de compensation. Durant la période d'anticipation, il n'existe pas de droit à une rente pour enfant. Ajournement de la rente : Les personnes qui ajournent leur retraite d'au moins un an et de cinq ans au maximum bénéficient d'une rente de vieilesse majorée d'une augmentation pendant toute la durée de leur retraite. Combinaison : Il est également possible de combiner l'anticipation et l'ajournement. Une partie de la rente de vieillesse peut être anticipée et une partie peut être ajournée une fois l'âge de référence atteint. Le montant de la réduction ou de la majoration de la rente est fixé selon le principe des calculs actuariels. Dans le cadre d'un couple, il est possible que l'un des conjoints anticipe son droit à la rente alors que l'autre l'ajourne.", "https://www.ahv-iv.ch/fr/Assurances-sociales/Assurance-vieillesse-et-survivants-AVS/Rentes-de-vieillesse#qa-1137"),
    ]

    embeddings = get_embedding([x[0] for x in texts])

    connection = create_db_connection()

    cursor = connection.cursor()

    try:
        for text, embedding in zip(texts, embeddings):
            embedding_values = embedding.to_dict()["embedding"]
            cursor.execute(
                "INSERT INTO embeddings (embedding, text, url, created_at, modified_at) VALUES (%s, %s, %s, %s, %s)",
                (embedding_values, text[0], text[1], datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
        connection.commit()
    except (Exception, psycopg2.Error) as error:
        raise HTTPException(status_code=500, detail="Error while writing to DB") from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return {"content": "RAG data indexed successfully"}

@app.post("/get_docs", summary="Retrieve context docs endpoint", response_description="Return context docs from semantic search", status_code=200)
async def get_docs(request: RAGRequest):

    query_embedding = get_embedding(request.query)[0]["embedding"]

    connection = create_db_connection()

    cursor = connection.cursor()

    try:
        cursor.execute(f"""
            SELECT text, url,  1 - (embedding <=> '{query_embedding}') AS cosine_similarity
            FROM embeddings
            ORDER BY cosine_similarity desc
            LIMIT 1
        """)
        for res in cursor.fetchall():
            print(f"Text: {res[0]}; URL: {res[1]}; Similarity: {res[2]}")
    except (Exception, psycopg2.Error) as error:
        raise HTTPException(status_code=500, detail="Error while performing semantic search") from error
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return {"contextDocs": res[0], "sourceUrl": res[1], "cosineSimilarity": res[2]}