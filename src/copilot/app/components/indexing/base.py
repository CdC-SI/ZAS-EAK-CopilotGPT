"""**Indexing** interface."""
import logging

from abc import ABC, abstractmethod
from typing import List, Any
import aiohttp

from haystack.dataclasses import Document

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Interface for scraping models."""

    async def get_sitemap(self, sitemap_url: str) -> bytes:
        """Get sitemap content from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sitemap_url, timeout=10) as response:
                    response.raise_for_status()
                    return await response.read()
        except aiohttp.ClientError as e:
            logger.error("Failed to fetch sitemap: %s", e)

    @abstractmethod
    def scrap_urls(self, url: List[str]) -> List[Any]:
        """Scrap HTML content from a list of URLs."""

    @abstractmethod
    def from_sitemap(self, sitemap_url: str) -> List[Any]:
        """Wrapper method to scrap HTML content from a sitemap.xml URL."""



class BaseParser(ABC):
    """Interface for parsing models."""

    @abstractmethod
    def extract_urls_from_xml(self, xml: bytes) -> List[str]:
        """Parse XML content."""

    @abstractmethod
    def convert_to_documents(self, content: List[Any]) -> List[Document]:
        """Convert HTML content to documents."""

    @abstractmethod
    def clean_documents(self, documents: List[Document]) -> List[Document]:
        """Clean documents."""
        return [doc for doc in documents if doc.content is not None]

    @abstractmethod
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        return [doc for doc in documents if doc.content is not None]


class BaseIndexer(ABC):
    """Interface for indexing models."""

    @abstractmethod
    def index_from_sitemap(self, sitemap_url: str) -> None:
        """Embed search docs."""

