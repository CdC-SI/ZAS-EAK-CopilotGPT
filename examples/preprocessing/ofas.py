# %%
import json
import logging
import pandas as pd
from typing import List, Any
from haystack.dataclasses import ByteStream, Document
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
import requests
from tqdm import tqdm
import re

# %%
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# %%
# Load the PDF URLs from the JSON file
with open('pdf_urls.json', 'r') as file:
    pdf_urls = json.load(file)
pdf_urls = pdf_urls[:20] + pdf_urls[460:480] + pdf_urls[-20:]

# %%
#TODO: generate tags for each pdf file

# %%
#TODO: generate tags for each pdf file

# %%
#TODO: generate summary for each pdf file

# %%
#TODO: generate hyq for each pdf file

# %%
#TODO: generate hyq declarative for each pdf file

# %%
# Define the parser class
class OFASParser:
    def __init__(self):
        self.pdf_converter = PyPDFToDocument()
        self.cleaner = DocumentCleaner(
            remove_empty_lines=True,
            remove_extra_whitespaces=True,
            remove_repeated_substrings=False,
        )
        self.splitter = DocumentSplitter(
            split_by="sentence",
            split_length=5,
            split_overlap=1,
            split_threshold=4,
        )

    def clean_text(self, text: str) -> str:
        # Remove excess dots and formatting artifacts
        text = re.sub(r'\.{4,}', '', text)  # Remove sequences of three or more dots
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single newline
        text = text.strip()  # Remove leading and trailing whitespace
        return text

    def convert_to_documents(self, pdf_urls: List[str]) -> List[dict]:
        documents = []
        for url in tqdm(pdf_urls, desc="Processing PDFs", unit="file"):
            try:
                # Fetch the PDF content
                response = requests.get(url)
                response.raise_for_status()

                # Check if the content is a PDF
                if response.headers.get('Content-Type') != 'application/pdf':
                    logger.warning(f"Skipping non-PDF content from {url}")
                    continue

                pdf_content = response.content

                # Convert PDF content to Document objects
                byte_stream = ByteStream(data=pdf_content)
                result = self.pdf_converter.run(sources=[byte_stream])
                converted_docs = result["documents"]  # Ensure this is a list of Document objects

                # Clean documents
                cleaned_result = self.cleaner.run(documents=converted_docs)
                cleaned_docs = cleaned_result["documents"]  # Extract the list of cleaned Document objects

                # Split documents
                split_result = self.splitter.run(documents=cleaned_docs)
                split_docs = split_result["documents"]  # Extract the list of split Document objects

                # Create document format for each converted document
                for doc in cleaned_docs:
                    # Clean the text content
                    cleaned_text = self.clean_text(doc.content)

                    # Extract language from the URL
                    language = url.split('/')[3]
                    document = {
                        "url": url,
                        "text": cleaned_text,
                        "language": language,
                        "tags": [],  # Leave empty for now
                        "subtopics": [],  # Leave empty for now
                        "summary": "",  # Leave empty for now
                        "doctype": "context_doc",  # Constant value
                        "organizations": "OFAS",  # Constant value
                        "hyq": "",  # Leave empty for now
                        "hyq_declarative": ""  # Leave empty for now
                    }
                    documents.append(document)
            except requests.RequestException as e:
                logger.error(f"Failed to fetch PDF from {url}: {e}")
        return documents

# %%
# Initialize the parser
ofas_parser = OFASParser()

# %%
# Process the PDF URLs
def process_pdfs():
    # Convert PDFs to documents
    documents = ofas_parser.convert_to_documents(pdf_urls)
    
    # Output the documents
    for doc in documents[:3]:
        print(doc)
    
    return documents


# %%
# Run the processing function
documents = process_pdfs()

# %%
# Save documents to a CSV file
df = pd.DataFrame(documents)  # Create a DataFrame from the list of documents
df.to_csv('output/ofas.csv', index=False)  # Save to CSV without the index


