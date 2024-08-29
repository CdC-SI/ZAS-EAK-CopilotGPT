import streamlit as st
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from random import sample

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

# Streamlit app
st.title('2D t-SNE Visualization of Embedding Vectors')

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

        # with col2:
        #     if init_method == "pca":
        #         init_method = "random"
        #     else:
        #         init_method = "pca"
        #     tsne_results_alt = compute_tsne(embeddings, perplexity, init_method)
        #     plot_tsne(tsne_results_alt, 't-SNE Projection 2 (Alternate Initialization)')
