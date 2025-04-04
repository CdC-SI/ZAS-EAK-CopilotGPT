"""**Indexing** interface."""

import logging

from abc import ABC, abstractmethod
from typing import List, Any
import aiohttp

from haystack.dataclasses import Document, ByteStream
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter

from sqlalchemy.orm import Session
from database.service.document import document_service
from schemas.document import DocumentCreate

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
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

    async def fetch(self, url: str) -> str:
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
            async with aiohttp.ClientSession(trust_env=True) as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    return await response.text()

        except aiohttp.ClientError as e:
            logger.error("Failed to fetch url '%s': %s", url, e)

    @abstractmethod
    def scrap_urls(self, urls: List[str]) -> List[Any]:
        """
        Abstract method to scrape HTML content from a list of URLs.

        Parameters
        ----------
        urls : list of str
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

    def __init__(self):
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

    def remove_empty_documents(self, documents: List[Any]) -> List[Any]:
        """
        Remove documents from the list that have their data attribute set to None.

        Parameters
        ----------
        documents : list
            Document objects to be filtered.

        Returns
        -------
        list
            Document objects where the content attribute is not None.
        """
        return [doc for doc in documents if doc.content is not None]

    def remove_duplicate_links(self, links):
        """
        Removes duplicate links from a list of tags.

        Parameters
        ----------
        links : list of bs4.element.Tag
            The list of tags to remove duplicates from.

        Returns
        -------
        list of bs4.element.Tag
            The list of tags without duplicates.
        """
        seen_hrefs = set()
        unique_tags = []
        for tag in links:
            href = tag["href"]
            if href not in seen_hrefs:
                seen_hrefs.add(href)
                unique_tags.append(tag)
        return unique_tags

    def contains_tag(self, tag):
        """
        Check if a tag contains a specific string.

        Parameters
        ----------
        tag : bs4.element.Tag
            The tag to check.

        Returns
        -------
        bool
            True if the tag contains the string, False otherwise.
        """
        pass

    def get_pdf_paths(self, soup):
        """
        Get the paths to PDF files from a BeautifulSoup object.

        Parameters
        ----------
        soup : BeautifulSoup
            The BeautifulSoup object to extract PDF paths from.

        Returns
        -------
        list of str
            The list of PDF paths.
        """
        pass

    @abstractmethod
    def parse_urls(self, content: str) -> List[str]:
        """
        Extracts URLs from the given content.

        Parameters
        ----------
        content : str
            The content to extract URLs from.

        Returns
        -------
        List[str]
            A list of URLs extracted from the content.
        """

    @abstractmethod
    def convert_to_documents(self, content: List[Any]) -> List[Any]:
        """
        Abstract method to convert some content to documents.

        Parameters
        ----------
        content : list of Any
            The content to convert.

        Returns
        -------
        list of Document
            The converted documents.
        """

    def clean_documents(self, documents: List[Document]) -> List[Document]:
        """
        Removes docs with None content and cleans the given documents.

        Parameters
        ----------
        documents : List[Document]
            The documents to clean.

        Returns
        -------
        List[Document]
            Cleaned documents.
        """
        return self.cleaner.run(documents=documents)

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Removes docs with None content and splits the given documents into chunks.

        Parameters
        ----------
        documents : List[Document]
            The documents to split into chunks.

        Returns
        -------
        List[Document]
            A list of documents split into chunks.
        """
        return self.splitter.run(documents=documents)


class BaseIndexer(ABC):
    """
    Abstract base class for indexing models.

    Methods
    -------
    index(sitemap_url: str) -> dict:
        Abstract method to index content from a URL into a vectorDB.
    """

    def __init__(self, scraper, parser):
        self.scraper = scraper
        self.parser = parser

    async def get_pages_from_sitemap(
        self, sitemap_url: str
    ) -> List[ByteStream]:
        # Get sitemap
        sitemap = await self.scraper.fetch(sitemap_url)

        # Extract URLs from sitemap
        url_list = self.parser.parse_urls(sitemap)

        # Get HTML from each URL
        return self.scraper.scrap_urls(url_list)

    @abstractmethod
    async def from_pages_to_content(
        self, pages: List[ByteStream]
    ) -> List[Any]:
        """
        Abstract method to convert URLs to content.

        Parameters
        ----------
        pages : List[ByteStream]
            The HTML pages to convert to content.

        Returns
        -------
        List[Any]
            The content extracted from the URLs.
        """

    async def get_content_from_pdf(self, content: List[Any]) -> List[Any]:
        """
        Extract content from PDFs.

        Parameters
        ----------
        content : List[Any]
            The content to extract from.

        Returns
        -------
        List[Any]
            The extracted content chunked.
        """
        # Convert content to Document objects
        documents = self.parser.convert_to_documents(content)

        # Remove empty documents
        documents = self.parser.remove_empty_documents(documents["documents"])

        # Clean documents
        documents = self.parser.clean_documents(documents)

        # Split documents into chunks
        chunks = self.parser.split_documents(documents["documents"])
        result = [
            {"text": chunk.content, "url": chunk.meta.get("url", None)}
            for chunk in chunks["documents"]
        ]

        return result

    async def add_content_to_db(
        self,
        db: Session,
        content: List[Any],
        source: str,
        user_uuid: str,
        language: str,
        embed: bool,
    ):
        """
        Add content to the database.

        Parameters
        ----------
        db : Session
            The database session to use.
        content : List[Any]
            Content to add to the database.
        source : str
            The source of the content.
        user_uuid : str
            The UUID of the user who added the content.
        language: str
            Language of the content.
        embed : bool
            Whether to embed the content.

        Returns
        -------
        dict
            content: Success message
        """
        # Convert content to Document objects
        documents = self.parser.convert_to_documents(content)

        # Remove empty documents
        documents = self.parser.remove_empty_documents(documents["documents"])

        # Clean documents
        documents = self.parser.clean_documents(documents)

        # Split documents into chunks
        chunks = self.parser.split_documents(documents["documents"])

        user_uuid = user_uuid if user_uuid else None

        # TO DO: refactor embedding logic to embed from documents (add from_documents method)
        # Upsert documents into VectorDB
        for doc in chunks["documents"]:
            text = doc.content
            logger.info(doc.meta)
            url = doc.meta["url"] if "url" in doc.meta else source
            await document_service.upsert(
                db,
                DocumentCreate(
                    url=url,
                    text=text,
                    source=source,
                    user_uuid=user_uuid,
                    language=language,
                ),
                embed=embed,
            )

    async def index(
        self, sitemap_url: str, db: Session, embed: bool = True
    ) -> dict:
        urls = await self.get_pages_from_sitemap(sitemap_url)
        content = await self.from_pages_to_content(urls)

        await self.add_content_to_db(
            db, content, source=sitemap_url, embed=embed
        )

        return {"content": f"{sitemap_url}: data indexed successfully"}
