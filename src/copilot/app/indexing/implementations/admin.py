import logging
from typing import List, Any

from haystack.dataclasses import Document
from haystack.components.converters import HTMLToDocument

from bs4 import BeautifulSoup

from indexing.base import BaseParser, BaseIndexer
from utils.embedding import get_embedding

from indexing import queries
from .scraper import scraper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdminParser(BaseParser):
    """
    A class used to parse, clean and split documents from a *.admin.ch website.

    Attributes
    ----------
    html_converter : HTMLToDocument
        An instance of HTMLToDocument to convert HTML content to Document objects.

    cleaner : DocumentCleaner
        An instance of DocumentCleaner to clean documents.

    splitter : DocumentSplitter
        An instance of DocumentSplitter to split documents into chunks.

    Methods
    -------
    parse_xml(sitemap: bytes) -> List[str]
        Extracts URLs from the given XML sitemap.

    convert_html_to_documents(content: List[ByteStream]) -> List[Document]
        Converts HTML content to Document objects.

    clean_documents(documents: List[Document]) -> List[Document]
        Cleans the given documents.

    split_documents(documents: List[Document]) -> List[Document]
        Splits the given documents into chunks.
    """
    def __init__(self):
        super().__init__()

    def parse_urls(self, content: str) -> List[str]:
        soup = BeautifulSoup(content, features="xml")

        url_list = []

        # Iterate over all 'url' elements and extract 'loc' URLs
        for url_element in soup.find_all('url'):
            loc_element = url_element.find('loc')
            if loc_element and loc_element.text:
                url_list.append(loc_element.text)

        return url_list

    def convert_to_documents(self, content: List[Any]) -> List[Any]:
        return HTMLToDocument().run(inputs=content)


class AdminIndexer(BaseIndexer):
    """
    A class used to index documents from *.admin.ch into a VectorDB.

    Attributes
    ----------
    scraper : Scraper
        An instance of Scraper to scrape URLs and extract content from them.
    parser : Parser
        An instance of Parser to parse and clean documents.
    embedding_client : Embedding
        An instance of Embedding to embed documents.

    Methods
    -------
    index(sitemap_url: str) -> dict
        Scraps, parses and indexes HTML webpage content from the given sitemap URL into the VectorDB.
    """
    # TO DO: index multiple languages: ["de", "fr", "it"]
    async def index(self, sitemap_url: str, proxy: str = None) -> dict:
        """
        Should implement the following steps:
        1. Fetch the sitemap content
        2. Parse the sitemap content (get URLs)
        3. Fetch HTML content for all URLs
        4. Convert HTML to Documents
        5. Clean the documents
        6. Split the documents
        7. Embed the documents
        8. Upsert the documents
        """

        # Get sitemap
        sitemap = await self.scraper.fetch(sitemap_url, proxy=proxy)

        # Extract URLs from sitemap
        url_list = self.parser.parse_urls(sitemap)

        # Scrap HTML from URLs
        content = self.scraper.scrap_urls(url_list)

        # Convert HTML content to Document objects
        documents = self.parser.convert_to_documents(content)

        # Remove empty documents
        documents = self.parser.remove_empty_documents(documents["documents"])

        # Clean documents
        documents = self.parser.clean_documents(documents)

        # Split documents into chunks
        chunks = self.parser.split_documents(documents["documents"])

        # TO DO: refactor embedding logic to embed from documents (add from_documents method)
        # Embed documents
        str_chunks = [doc.content for doc in chunks["documents"]]
        # document_embeddings = get_embedding(str_chunks)[0].embedding
        document_embeddings = []
        urls = [doc.meta["url"] for doc in chunks["documents"]]

        # Upsert documents into VectorDB
        for embedding, doc, url in zip(document_embeddings, str_chunks, urls):
            await queries.insert_rag(str(embedding), doc, url)

        return {"content": f"{sitemap_url}: RAG data indexed successfully"}


admin_indexer = AdminIndexer(
    scraper=scraper,
    parser=AdminParser()
)
