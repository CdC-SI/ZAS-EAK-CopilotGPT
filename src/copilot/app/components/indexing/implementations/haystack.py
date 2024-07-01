import logging
from typing import List
import xml.etree.ElementTree as ET
from datetime import datetime

from haystack.dataclasses import Document, ByteStream
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter

from components.indexing.base import BaseScraper, BaseParser, BaseIndexer
from components.embedding.factory import EmbeddingFactory

from indexing import queries

# Load env variables
from config.base_config import rag_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HaystackScraper(BaseScraper):

    def __init__(self):
        super().__init__()
        self.fetcher = LinkContentFetcher()

    def scrap_urls(self, url_list: List[str]) -> List[ByteStream]:
        streams = self.fetcher.run(urls=url_list)
        return streams["streams"]

    async def from_sitemap(self, sitemap_url: str) -> List[ByteStream]:

        # Get sitemap
        sitemap = await self.get_sitemap(sitemap_url)

        # Extract URLs from sitemap
        url_list = HaystackParser.extract_urls_from_xml(sitemap)

        # Scrap HTML from URLs
        content = self.scrap_urls(url_list)

        return content


class HaystackParser(BaseParser):

    def __init__(self):
        self.converter = HTMLToDocument()
        self.cleaner = DocumentCleaner(
            remove_empty_lines=True,
            remove_extra_whitespaces=True,
            remove_repeated_substrings=False
        )
        self.splitter = DocumentSplitter(
            split_by="passage",
            split_length=1,
            split_overlap=0
        )

    @staticmethod
    def extract_urls_from_xml(sitemap: bytes) -> List[str]:

        # Parse XML sitemap and extract web page URLs
        tree = ET.ElementTree(ET.fromstring(sitemap))
        root = tree.getroot()

        # Define the namespace dictionary
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # List to store all URLs
        url_list = []

        # Iterate over all 'url' elements and modify 'loc' sub-elements
        for url_element in root.findall('ns:url', namespaces):
            loc_element = url_element.find('ns:loc', namespaces)
            if loc_element is not None and loc_element.text:
                url_list.append(loc_element.text)

        return url_list

    def convert_to_documents(self, content: List[ByteStream]) -> List[Document]:

        return self.converter.run(sources=content)

    def clean_documents(self, documents: List[Document]) -> List[Document]:

        return self.cleaner.run(documents=documents['documents'])

    def split_documents(self, documents: List[Document]) -> List[Document]:

        return self.splitter.run(documents=documents['documents'])




class HaystackIndexer(BaseIndexer):

    def __init__(self):
        self.scraper = HaystackScraper()
        self.parser = HaystackParser()
        self.embedding_client = EmbeddingFactory.get_embedding_client(rag_config["embedding"]["model"])

    async def index_from_sitemap(self, sitemap_url: str) -> dict:

        # Get content from sitemap
        content = await self.scraper.from_sitemap(sitemap_url)

        # Convert HTML content to Document objects
        documents = self.parser.convert_to_documents(content)

        # Clean documents
        documents = self.parser.clean_documents(documents)

        # Split documents into chunks
        chunks = self.parser.split_documents(documents)

        # TO DO: refactor embedding logic to embed from documents (add from_documents method)
        # Embed documents
        str_chunks = [doc.content for doc in chunks["documents"]]
        document_embeddings = self.embedding_client.embed_documents(str_chunks)
        document_embeddings = [e.embedding for e in document_embeddings]
        urls = [doc.meta["url"] for doc in chunks["documents"]]

        # Upsert documents into VectorDB
        for embedding, doc, url in zip(document_embeddings, str_chunks, urls):
            date = datetime.now()
            await queries.insert_rag(str(embedding), doc, url, date, date)

        return {"content": "RAG data indexed successfully"}
