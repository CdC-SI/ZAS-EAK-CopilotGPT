import os
from dotenv import load_dotenv
load_dotenv()
from typing import List, Union

import openai
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from numpy import dot
from numpy.linalg import norm
from sklearn.manifold import TSNE
from random import sample

from database.service import document_service
from config.clients_config import clientEmbed

import logging
logger = logging.getLogger(__name__)

# Load environment variables
POSTGRES_USER = os.environ.get("POSTGRES_USER", None)
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", None)
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", None)
POSTGRES_DB = os.environ.get("POSTGRES_DB", None)
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", None)

# Cosine similarity function
def cosine_sim(a, b):
    return dot(a, b) / (norm(a) * norm(b))

# Function to get embeddings from OpenAI API
def get_embedding(text: Union[List[str], str], embedding_models):
    try:
        embedding = []
        for model in embedding_models:
            response = clientEmbed.embeddings.create(
                input=text,
                model=model,
            )
            embedding.append(response.data[0].embedding)
        return embedding
    except openai.BadRequestError as e:
        logger.error(e.message)
        logger.error(f"Failed to get embeddings for text of length: {len(text)}")
        return None

def plot_cos_sim(d_embedding, q_embedding, embedding_models, run_name):
    if q_embedding is None or d_embedding is None:
        st.error("Please generate both query and document embeddings before plotting.")
        return

    # Calculate new cosine similarities
    new_cos_sim = []
    for q_e, d_e in zip(q_embedding, d_embedding):
        new_cos_sim.append(cosine_sim(q_e, d_e))

    # Initialize or update session state for cosine similarities
    if "cos_sim_history" not in st.session_state:
        st.session_state.cos_sim_history = []
    if "run_name" not in st.session_state:
        st.session_state.run_name = []
    if "cos_sim_table" not in st.session_state:
        # Initialize an empty DataFrame for the table
        st.session_state.cos_sim_table = pd.DataFrame(columns=["run_name"] + embedding_models)

    # Create a new DataFrame for the new row
    new_row = pd.DataFrame({
        "run_name": [run_name],
        embedding_models[0]: [new_cos_sim[0]],
        embedding_models[1]: [new_cos_sim[1]],
        embedding_models[2]: [new_cos_sim[2]],
    })

    # Append the new cosine similarity values to the session history
    st.session_state.cos_sim_history.append(new_cos_sim)
    st.session_state.run_name.append(run_name)
    st.session_state.cos_sim_table = pd.concat([st.session_state.cos_sim_table, new_row], ignore_index=True)

    # Display the cosine similarity table
    st.table(st.session_state.cos_sim_table)

    # Plot the current and previous cosine similarities
    fig1, ax = plt.subplots(figsize=(20, 5))  # Wider figure for more room

    num_groups = len(st.session_state.cos_sim_history)
    num_models = len(embedding_models)

    bar_width = 0.05

    # Adjust the positions of the bars so they touch within each group
    for idx, cos_sim in enumerate(st.session_state.cos_sim_history):
        ax.bar(
            x=[i + idx * bar_width for i in range(len(cos_sim))],  # Bars will touch with no spacing
            height=cos_sim,
            width=bar_width,  # Bars are wider and adjacent
            label=st.session_state.run_name[idx]
        )

    # Set x-axis labels and ticks
    ax.set_xticks([i + (num_groups - 1) * bar_width / 2 for i in range(num_models)])
    ax.set_xticklabels(embedding_models, rotation=45)
    ax.legend(title="Embedding Runs")

    # Display the plot
    st.pyplot(fig1)

    return new_cos_sim

# Function to compute t-SNE
def compute_tsne(embeddings, perplexity, init, n_iter, learning_rate):
    tsne = TSNE(n_components=2,
                perplexity=perplexity,
                init=init,
                random_state=42,
                n_iter_without_progress=250,
                n_iter=n_iter,
                metric='cosine',
                learning_rate=learning_rate,
                method='exact')
    tsne_results = tsne.fit_transform(embeddings)
    return tsne_results

# Function to plot t-SNE results
def plot_tsne(tsne_results, labels, title):
    colors = sample(list(mcolors.CSS4_COLORS.keys()), len(labels))
    fig, ax = plt.subplots()
    for i, (txt_query, txt_answer) in enumerate(zip(labels[:10], labels[10:])):
        ax.scatter(tsne_results[i, 0], tsne_results[i, 1], color=colors[i])
        ax.scatter(tsne_results[i+10, 0], tsne_results[i+10, 1], color=colors[i])
        ax.annotate(txt_query, (tsne_results[i, 0], tsne_results[i, 1]))
        ax.annotate(txt_answer, (tsne_results[i+10, 0], tsne_results[i+10, 1]))
    ax.set_title(title)
    ax.set_xlabel('t-SNE 1')
    ax.set_ylabel('t-SNE 2')
    st.pyplot(fig)

# Get database session
def get_db():
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db

db = get_db()

embedding_models = ["text-embedding-ada-002", "text-embedding-3-small", "text-embedding-3-large"]

# Main Streamlit app
def main():
    st.set_page_config(layout="wide")
    tab1, tab2 = st.tabs(["Embeddings", "Preprocessing Eval"])

    with tab1:
        st.title("Embeddings Playground")
        st.write("Test how a document can get higher cosine similarity to a query by editing the document text. The idea is to maximize the cosine similarity between the query and the document which can answer the query.")

        col1, col2 = st.columns([0.3, 0.7])

        # Initialize session state for embeddings and document text
        if "q_embedding" not in st.session_state:
            st.session_state.q_embedding = None
        if "d_embedding" not in st.session_state:
            st.session_state.d_embedding = None
        if "document_text" not in st.session_state:
            st.session_state.document_text = ""

        # Test query
        with col1:
            st.header("1. Query")
            query = st.text_input("Query")

            # Recompute embeddings when "Embed Query" button is clicked
            if st.button("Embed Query"):
                st.session_state.q_embedding = get_embedding(query, embedding_models)
                st.success("Query embeddings updated!")

            # Document search
            st.header("2. Document Search")
            document = None

            # Text search
            text_input = st.text_input("Search for documents by text")
            if text_input:
                document = document_service.search_by_text(db, text_input)[0]
                st.session_state.document_text = document.text

            # URL search
            document_url_input = st.text_input("Get document by URL", value="https://ahv-iv.ch/p/1.01.f")
            if document_url_input:
                document = document_service.get_by_url(db, document_url_input)
                st.session_state.document_text = document.text

            if document:
                st.subheader("Document Metadata")
                st.write(f"Doc ID: {document.id}")
                st.write(f"Doc Language: {document.language}")

        # Display document in text area and embed when button clicked
        with col2:
            st.header("3. Edit Document")
            edited_document_text = st.text_area("Document:", value=st.session_state.document_text, height=500)

            # Name for edited document run
            run_name = st.text_input("Edit Description", value="")

            # Re-embed document with updated text
            if st.button("Embed Document"):
                st.session_state.document_text = edited_document_text
                st.session_state.d_embedding = get_embedding(st.session_state.document_text, embedding_models)
                st.success("Document embeddings updated!")

        # Visualization section
        st.header("4. Visualizations")
        st.write("Cosine Similarity Barplot")
        if st.button("Plot"):
            cos_sim = plot_cos_sim(st.session_state.d_embedding, st.session_state.q_embedding, embedding_models, run_name)

    with tab2:
        st.title("Preprocessing Evaluation")
        st.write("Try out different preprocessing techniques on your dataset and run a retrieval evaluation to see how you can improve retrieval through data preprocessing.")

        st.header('2D t-SNE Visualization of Embedding Vectors')

        # Upload CSV file
        uploaded_file = st.file_uploader("Upload CSV file", type="csv")

        if uploaded_file is not None:
            # Load CSV file
            data = pd.read_csv(uploaded_file, index_col=False)

            st.write("Data Preview:")
            st.write(data.head())
            st.write(f"Embedding dimension: {data.shape[1]-1}")
            st.write(f"n_samples: {data.shape[0]}")

            # Check if the CSV contains embeddings
            if data.shape[1] < 2:
                st.error("The uploaded CSV file must contain at least two columns.")
            else:
                # Get the perplexity value from slider
                perplexity = st.slider('Perplexity', min_value=5, max_value=50, value=data.shape[0]-1, step=1)

                # Select initialization method
                init_method = st.selectbox("Initialization Method", ["pca", "random"])

                # Select n_iter
                n_iter = st.slider("Optimization Iterations", min_value=100, max_value=3000, value=1000, step=100)

                # Select learning rate
                learning_rate = st.slider("Learning Rate", min_value=10, max_value=3000, value=1000, step=100)

                # Extract embeddings from the CSV file
                embeddings = data[[col for col in data.columns if data[col].dtype==float]]
                labels = data.label

                # Plot the results
                #col1, col2 = st.columns(2)
                col1, col2 = st.columns(2)

                with col1:
                    # Compute t-SNE projections
                    tsne_results = compute_tsne(embeddings, perplexity, init_method, n_iter, learning_rate)
                    plot_tsne(tsne_results, labels, 't-SNE Projection')

if __name__ == "__main__":
    main()