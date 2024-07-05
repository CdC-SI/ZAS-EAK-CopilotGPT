import logging
from typing import List
from urllib.parse import unquote

from haystack.dataclasses import Document, ByteStream
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument, PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.preprocessors import DocumentSplitter

from indexing.base import BaseScraper, BaseParser, BaseIndexer
from models.embedding.factory import EmbeddingFactory

from indexing import queries

# Load env variables
from config.base_config import rag_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Scraper(BaseScraper):
    """
    A class used to scrap URLs from *.admin.ch websites.

    Attributes
    ----------
    fetcher : LinkContentFetcher
        An instance of LinkContentFetcher to fetch the content of URLs.

    Methods
    -------
    scrap_urls(url_list: List[str]) -> List[ByteStream]
        Scrapes the given URLs and returns the content as a list of ByteStreams.

    """

    def __init__(self):
        super().__init__()
        self.fetcher = LinkContentFetcher()

    def scrap_urls(self, url_list: List[str]) -> List[ByteStream]:
        """
        Scrapes the given URLs and returns the content as a list of ByteStreams.

        Parameters
        ----------
        url_list : List[str]
            A list of URLs to scrape.

        Returns
        -------
        List[ByteStream]
            A list of ByteStreams containing the content of the scraped URLs.
        """
        streams = self.fetcher.run(urls=url_list)
        return streams["streams"]


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
        self.html_converter = HTMLToDocument()
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

    def parse_xml(self, sitemap: bytes) -> List[str]:
        """
        Extracts URLs from the given XML sitemap.

        Parameters
        ----------
        sitemap : bytes
            The XML sitemap to extract URLs from.

        Returns
        -------
        List[str]
            A list of URLs extracted from the sitemap.
        """
        soup = self.get_soup(sitemap, "xml")

        url_list = []

        # Iterate over all 'url' elements and extract 'loc' URLs
        for url_element in soup.find_all('url'):
            loc_element = url_element.find('loc')
            if loc_element and loc_element.text:
                url_list.append(loc_element.text)

        return url_list

    def parse_html(self):
        pass

    def contains_tag(self):
        pass

    def convert_html_to_documents(self, content: List[ByteStream]) -> List[Document]:
        """
        Converts HTML content to Document objects.

        Parameters
        ----------
        content : List[ByteStream]
            The HTML content to convert to Document objects.

        Returns
        -------
        List[Document]
            A list of Document objects created from the HTML content.
        """
        return self.html_converter.run(sources=content)

    def convert_pdf_to_documents(self):
        pass

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
            A list of cleaned documents.
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



class AHVParser(BaseParser):
    """
    A class used to parse and clean documents.

    Attributes
    ----------
    pdf_converter : PyPDFToDocument
        An instance of PyPDFToDocument to convert PDF content to Document objects.

    cleaner : DocumentCleaner
        An instance of DocumentCleaner to clean documents.

    splitter : DocumentSplitter
        An instance of DocumentSplitter to split documents into chunks.

    Methods
    -------
    parse_html(html: bytes) -> List[str]
        Extracts URLs from the given HTML content.

    convert_pdf_to_documents(content: List[ByteStream]) -> List[Document]
        Converts PDF content to Document objects.

    clean_documents(documents: List[Document]) -> List[Document]
        Cleans the given documents.

    split_documents(documents: List[Document]) -> List[Document]
        Splits the given documents into chunks.
    """
    def __init__(self):
        self.pdf_converter = PyPDFToDocument()
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

    def parse_xml(self):
        pass

    def contains_tag(self, tag):
        """
        Checks if a tag contains a memento URL.

        Parameters
        ----------
        tag : bs4.element.Tag
            The tag to check.

        Returns
        -------
        bool
            True if the tag contains a memento URL, False otherwise.
        """
        if tag.name == "a" and "href" in tag.attrs:
            href = tag["href"]
            decoded_href = unquote(href)
            return "Merkblätter/" in decoded_href
        return False

    def get_pdf_paths(self, soup):
        """
        Extracts the paths of PDF documents from a BeautifulSoup object.

        Parameters
        ----------
        soup : BeautifulSoup
            The BeautifulSoup object to extract PDF paths from.

        Returns
        -------
        list of str
            The list of PDF paths.
        """
        # TO DO: re-scrap links which are not PDFs such as:
        # pdf_paths = [a["href"] for a in soup.find_all("a", {"class": "co-document-content"})]
        pdf_paths = [a["href"] for a in soup.find_all("a", {"class": "co-document-content"}) if "/p/" in a["href"]]
        return pdf_paths

    def parse_html(self, html: bytes) -> List[str]:
        """
        Extracts URLs from the given HTML content.

        Parameters
        ----------
        html : bytes
            The HTML content to extract URLs from.

        Returns
        -------
        List[str]
            A list of URLs extracted from the HTML content.
        """
        soup = self.get_soup(html, "html.parser")

        # Find all "a" tags with href containing "Merkblätter/" (and subsequent path)
        links = soup.find_all(self.contains_tag)

        # Remove duplicate links
        links = self.remove_duplicate_links(links)

        links = [link["href"] for link in links]

        return links

    def convert_html_to_documents(self):
        pass

    def convert_pdf_to_documents(self, content: List[ByteStream]) -> List[Document]:
        """
        Converts PDF content to Document objects.

        Parameters
        ----------
        content : List[ByteStream]
            The PDF content to convert to Document objects.

        Returns
        -------
        List[Document]
            A list of Document objects created from the PDF content.
        """
        return self.pdf_converter.run(sources=content)

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
            A list of cleaned documents.
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
    def __init__(self, parser: BaseParser, scraper: BaseScraper):
        self.scraper = scraper
        self.parser = parser
        self.embedding_client = EmbeddingFactory.get_embedding_client(rag_config["embedding"]["model"])

    # TO DO: index multiple languages: ["de", "fr", "it"]
    async def index(self, sitemap_url: str) -> dict:
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
        sitemap = await self.scraper.fetch(sitemap_url)

        # Extract URLs from sitemap
        url_list = self.parser.parse_xml(sitemap)

        # Scrap HTML from URLs
        content = self.scraper.scrap_urls(url_list)

        # Convert HTML content to Document objects
        documents = self.parser.convert_html_to_documents(content)

        # Remove empty documents
        documents = self.parser.remove_empty_documents(documents["documents"])

        # Clean documents
        documents = self.parser.clean_documents(documents)

        # Split documents into chunks
        chunks = self.parser.split_documents(documents["documents"])

        # TO DO: refactor embedding logic to embed from documents (add from_documents method)
        # Embed documents
        str_chunks = [doc.content for doc in chunks["documents"]]
        document_embeddings = self.embedding_client.embed_documents(str_chunks)
        document_embeddings = [e.embedding for e in document_embeddings]
        urls = [doc.meta["url"] for doc in chunks["documents"]]

        # Upsert documents into VectorDB
        for embedding, doc, url in zip(document_embeddings, str_chunks, urls):
            await queries.insert_rag(str(embedding), doc, url)

        return {"content": f"{sitemap_url}: RAG data indexed successfully"}


class AHVIndexer(BaseIndexer):
    """
    A class used to index PDF Merkblätter documents into a VectorDB.

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
        Scraps, parses and indexes PDF content from the given sitemap URL into the VectorDB.
    """
    def __init__(self, parser: BaseParser, scraper: BaseScraper):
        self.scraper = scraper
        self.parser = parser
        self.embedding_client = EmbeddingFactory.get_embedding_client(rag_config["embedding"]["model"])

    async def index(self, sitemap_url: str) -> dict:

        # Get sitemap
        sitemap = await self.scraper.fetch(sitemap_url)

        # Extract URLs of memento sections from sitemap (Allgemeines, Beiträge, etc.)
        url_list = self.parser.parse_html(sitemap)

        # Get HTML from each memento section link
        response = self.scraper.scrap_urls(url_list)

        soups = []
        for res in response:
            soups.append(self.parser.get_soup(res.data, "html.parser"))

        # Get PDF paths from each memento section
        pdf_paths = []
        for soup in soups:
            pdf_paths.extend(self.parser.get_pdf_paths(soup))

        # Scrap PDFs from each memento section
        pdf_urls = ["https://ahv-iv.ch" + pdf_path for pdf_path in pdf_paths]

        # Add "it", "fr" pdf paths
        pdf_urls.extend([pdf_url.replace(".d", ".f") for pdf_url in pdf_urls])
        pdf_urls.extend([pdf_url.replace(".d", ".i") for pdf_url in pdf_urls])

        content = self.scraper.scrap_urls(pdf_urls)

        # Convert PDF content to Document objects
        documents = self.parser.convert_pdf_to_documents(content)

        # Remove empty documents
        documents = self.parser.remove_empty_documents(documents["documents"])

        # Clean documents
        documents = self.parser.clean_documents(documents)

        # Split documents into chunks
        chunks = self.parser.split_documents(documents["documents"])

        # TO DO: refactor embedding logic to embed from documents (add from_documents method)
        # Embed documents
        str_chunks = [doc.content for doc in chunks["documents"]]
        document_embeddings = self.embedding_client.embed_documents(str_chunks)
        document_embeddings = [e.embedding for e in document_embeddings]
        urls = [doc.meta["url"] for doc in chunks["documents"]]

        # Upsert documents into VectorDB
        for embedding, doc, url in zip(document_embeddings, str_chunks, urls):
            await queries.insert_rag(str(embedding), doc, url)

        return {"content": f"{sitemap_url}: PDF RAG data indexed successfully"}



# Init scraper, parser, indexer for *.admin.ch and ahv-iv.ch
scraper = Scraper()
admin_parser = AdminParser()
ahv_parser = AHVParser()

admin_indexer = AdminIndexer(
    scraper=scraper,
    parser=admin_parser
)

ahv_indexer = AHVIndexer(
    scraper=scraper,
    parser=ahv_parser
)