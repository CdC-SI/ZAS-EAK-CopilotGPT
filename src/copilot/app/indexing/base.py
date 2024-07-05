"""**Indexing** interface."""
import logging

from abc import ABC, abstractmethod
from typing import List, Any
import aiohttp

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class for scraping models.

    Methods
    -------
    fetch(url: str) -> bytes:
        Fetches the content from a given URL.
    scrap_urls(url: List[str]) -> List[Any]:
        Abstract method to scrape HTML content from a list of URLs.
    html_content_from_sitemap(sitemap_url: str) -> List[Any]:
        Abstract method to scrape HTML content from a sitemap.xml URL.
    pdf_content_from_sitemap(sitemap_url: str) -> List[Any]:
        Abstract method to scrape PDF content from a specific sitemap URL.
    """

    async def fetch(self, url: str) -> bytes:
        """
        Fetches the content from a given URL.

        Parameters
        ----------
        url : str
            The URL to fetch content from.

        Returns
        -------
        bytes
            The content of the URL.

        Raises
        ------
        aiohttp.ClientError
            If the fetch operation fails.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    return await response.read()
        except aiohttp.ClientError as e:
            logger.error("Failed to fetch url '%s': %s", url, e)

    @abstractmethod
    def scrap_urls(self, url: List[str]) -> List[Any]:
        """
        Abstract method to scrape HTML content from a list of URLs.

        Parameters
        ----------
        url : list of str
            The URLs to scrape content from.

        Returns
        -------
        list of Any
            The scraped content.
        """



class BaseParser(ABC):
    """
    Abstract base class for parsing models.

    Methods
    -------
    parse_xml(xml: bytes) -> List[str]:
        Abstract method to parse XML content.
    parse_html(html: bytes) -> List[str]:
        Abstract method to parse HTML content.
    convert_html_to_documents(content: List[Any]) -> List[Document]:
        Abstract method to convert HTML content to documents.
    convert_pdf_to_documents(content: List[Any]) -> List[Document]:
        Abstract method to convert PDF content to documents.
    clean_documents(documents: List[Document]) -> List[Document]:
        Abstract method to clean documents.
    split_documents(documents: List[Document]) -> List[Document]:
        Abstract method to split documents into chunks.
    """

    def remove_empty_documents(self, documents: List[Any]) -> List[Any]:
        """
        Remove documents from the list that have their data attribute set to None.

        Parameters
        ----------
        documents : list
            List of document objects to be filtered.

        Returns
        -------
        list
            List of document objects where the content attribute is not None.
        """
        return [doc for doc in documents if doc.content is not None]

    @abstractmethod
    def parse_xml(self, xml: bytes) -> List[str]:
        """
        Abstract method to parse XML content.

        Parameters
        ----------
        xml : bytes
            The XML content to parse.

        Returns
        -------
        list of str
            The extracted content.
        """

    @abstractmethod
    def parse_html(self, html: bytes) -> List[str]:
        """
        Abstract method to parse HTML content.

        Parameters
        ----------
        html : bytes
            The HTML content to parse.

        Returns
        -------
        list of str
            The extracted content.
        """

    @abstractmethod
    def convert_html_to_documents(self, content: List[Any]) -> List[Any]:
        """
        Abstract method to convert HTML content to documents.

        Parameters
        ----------
        content : list of Any
            The HTML content to convert.

        Returns
        -------
        list of Document
            The converted documents.
        """

    @abstractmethod
    def convert_pdf_to_documents(self, content: List[Any]) -> List[Any]:
        """
        Abstract method to convert PDF content to documents.

        Parameters
        ----------
        content : list of Any
            The PDF content to convert.

        Returns
        -------
        list of Document
            The converted documents.
        """

    @abstractmethod
    def clean_documents(self, documents: List[Any]) -> List[Any]:
        """
        Abstract method to clean documents.

        Parameters
        ----------
        documents : list of Document
            The documents to clean.

        Returns
        -------
        list of Document
            The cleaned documents.
        """

    @abstractmethod
    def split_documents(self, documents: List[Any]) -> List[Any]:
        """
        Abstract method to split documents into chunks.

        Parameters
        ----------
        documents : list of Document
            The documents to split.

        Returns
        -------
        list of Document
            The split documents.
        """


class BaseIndexer(ABC):
    """
    Abstract base class for indexing models.

    Methods
    -------
    index(sitemap_url: str) -> dict:
        Abstract method to index content from a URL into a vectorDB.
    """

    @abstractmethod
    async def index(self, url: str) -> dict:
        """
        Abstract method to index content from a URL into a vectorDB.

        Parameters
        ----------
        sitemap_url : str
            The URL to index content from.

        Returns
        -------
        dict
            content: Success message
        """