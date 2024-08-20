import logging
from typing import List, Any

from haystack.components.converters import HTMLToDocument

from bs4 import BeautifulSoup

from haystack.dataclasses import ByteStream
from indexing.base import BaseParser, BaseIndexer
from indexing.scraper import scraper

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
        return HTMLToDocument().run(sources=content)


class AdminIndexer(BaseIndexer):
    """
    A class used to index documents from *.admin.ch into a VectorDB.

    Attributes
    ----------
    scraper : Scraper
        An instance of Scraper to scrape URLs and extract content from them.
    parser : Parser
        An instance of Parser to parse and clean documents.

    Methods
    -------
    index(sitemap_url: str) -> dict
        Scraps, parses and indexes HTML webpage content from the given sitemap URL into the VectorDB.
    """

    async def from_pages_to_content(self, pages: List[ByteStream]) -> List[Any]:
        return pages


admin_indexer = AdminIndexer(
    scraper=scraper,
    parser=AdminParser()
)
