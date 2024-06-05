import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
from lxml import etree

import queries

class WebScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def run(self, from_main: bool = False):
        """
        Asynchronously retrieves and processes FAQ data from 'https://faq.bsv.admin.ch' to insert into the database.

        The endpoint 'https://faq.bsv.admin.ch/sitemap.xml' is utilized to discover all relevant FAQ URLs. For each URL,
        the method extracts the primary question (denoted by the 'h1' tag) and its corresponding answer (within an 'article' tag).
        Unnecessary boilerplate text will be removed for clarity and conciseness.

        Each extracted FAQ entry is then upserted (inserted or updated if already exists) into the database, with detailed
        logging to track the operation's progress and identify any errors.

        Returns a confirmation message upon successful completion of the process.

        TODO:
        - Consider implementing error handling at a more granular level to retry failed insertions or updates, enhancing the robustness of the data ingestion process.
        - Explore optimization opportunities in text extraction and processing to improve efficiency and reduce runtime, especially for large sitemaps.
        """
        self.logger.info(f"Beginne Datenextraktion für: {self.base_url}")
        urls = self.get_sitemap_urls()

        if from_main:
            urls = urls[:9]

        for url in urls:
            h1, article, lang = self.extract(url)

            # Efficient text processing
            for term in ['Antwort\n', 'Rispondi\n', 'Réponse\n']:
                article = article.replace(term, '')

            if from_main:
                self.logger.info("--------------------")
                self.logger.info(f"url: {url}")
                self.logger.info(f"question: {h1}")
                self.logger.info(f"answer: {article}")
                self.logger.info(f"language: {lang}")

            elif h1 and article:
                self.logger.info(f"extract: {url}")
                info, rid = await queries.update_or_insert(url, h1, article, lang)
                self.logger.info(f"{info}: {url}")

        self.logger.info(f"Done! {len(urls)} wurden verarbeitet.")
        return urls

    def get_response(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        """Send a GET request and return the response object."""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None

    def get_sitemap_urls(self) -> List[str]:
        """Extract URLs from the sitemap."""
        response = self.get_response(self.base_url)
        if not response:
            return []

        root = etree.fromstring(response.content)
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [url.text for url in root.xpath("//sitemap:loc", namespaces=namespace)]

        return urls

    def extract(self, url: str):
        response = self.get_response(url)
        if not response:
            return ''

        soup = BeautifulSoup(response.text, 'lxml')

        extracted = []
        for tag in ['h1', 'article', 'html']:
            element = soup.find(tag)

            if tag == 'html':
                extracted += element['lang'] if element and element.has_attr('lang') else ''
            else:
                extracted += '\n'.join(line.strip() for line in element.get_text().splitlines() if line) if element else ''

        return extracted[0], extracted[1], extracted[2]

    def extract_text_from_tag(self, url: str, tag: str) -> str:
        """Extract text from a specific tag in a web page."""
        response = self.get_response(url)
        if not response:
            return ''

        soup = BeautifulSoup(response.text, 'lxml')
        body = soup.find(tag)
        return '\n'.join(line.strip() for line in body.get_text().splitlines() if line) if body else ''

    def detect_language(self, url: str) -> str:
        """Detect the language of a website based on the 'lang' attribute in the HTML tag."""
        response = self.get_response(url)
        if not response:
            return ''

        soup = BeautifulSoup(response.text, 'lxml')
        html_tag = soup.find('html')
        return html_tag['lang'] if html_tag and html_tag.has_attr('lang') else ''


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    sitemap_url = 'https://faq.bsv.admin.ch/sitemap.xml'
    scraper = WebScraper(sitemap_url)
    scraper.run(True)
