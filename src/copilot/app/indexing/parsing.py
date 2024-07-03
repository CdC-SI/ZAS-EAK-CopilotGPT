from bs4 import BeautifulSoup
from urllib.parse import unquote

def get_soup(response, parser: str = "html.parser"):
    """
    Parses the HTML response using BeautifulSoup.

    Parameters
    ----------
    response : str
        The HTML response to parse.
    parser : str, optional
        The parser library to use. Defaults to "html.parser".

    Returns
    -------
    BeautifulSoup
        The parsed HTML response.
    """
    return BeautifulSoup(response, features=parser)

def contains_memento_url(tag):
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

def remove_duplicate_links(links):
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
        href = tag['href']
        if href not in seen_hrefs:
            seen_hrefs.add(href)
            unique_tags.append(tag)
    return unique_tags

def get_pdf_paths(soup):
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