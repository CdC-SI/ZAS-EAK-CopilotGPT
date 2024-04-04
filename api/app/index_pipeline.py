import requests
import logging
from typing import List
from lxml import etree
from bs4 import BeautifulSoup

def get_sitemap_urls(sitemap_url: str) -> List[str]:
    """
    Extract URLs from the sitemap.
    
    :param sitemap_url: The URL of the sitemap to parse.
    :return: A list of extracted URLs.
    """
    response = requests.get(sitemap_url)
    if response.status_code != 200:
        return []
    
    root = etree.fromstring(response.content)
    namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [url.text for url in root.xpath("//sitemap:loc", namespaces=namespace)]
    
    return urls

def extract_text_from_url(url: str, tag: str) -> str:
    """
    Extract text from a specific tag in a web page.
    
    :param url: Web page URL.
    :param tag: HTML tag to extract text from.
    :return: Extracted text or an empty string if not found or on error.
    """
    try:
        with requests.Session() as session:
            response = session.get(url, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses
            
            soup = BeautifulSoup(response.text, 'lxml')  # Using 'lxml' for parsing for better performance
            body = soup.find(tag)
            return '\n'.join(line.strip() for line in body.get_text().splitlines() if line) if body else ''
    except (requests.HTTPError, requests.ConnectionError):
        # Handle specific exceptions and log them if needed
        return ''
    
    return ''

if __name__ == '__main__':
    sitemap_url = 'https://faq.bsv.admin.ch/sitemap.xml'

    # Logger configuration
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Beginne Datenextraktion für: {sitemap_url}")

    urls = get_sitemap_urls(sitemap_url)
    
    for url in urls[:9]:
        extracted_h1 = extract_text_from_url(url, 'h1')
        extracted_article = extract_text_from_url(url, 'article')
        
        # Efficient text processing
        for term in ['Antwort\n', 'Rispondi\n', 'Réponse\n']:
            extracted_article = extracted_article.replace(term, '')
        
        if extracted_h1:
            logger.info(f"url: {url}")
            logger.info(f"question: {extracted_h1}")
            logger.info(f"answer: {extracted_article}")
