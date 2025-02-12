import re


def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1) if match else ""


def remove_file_extension(filename):
    """
    Removes the file extension from the given filename.
    """
    return re.sub(
        r"\.(docx|pdf|xml|csv|xlsx)", "", filename, flags=re.IGNORECASE
    )


def clean_text(text):
    # Remove substrings starting with a timestamp (first digit) and ending with "- user" or "- assistant"
    text = re.sub(r"(?<!\S)\d[^\n]*?-(?: user| assistant)\n", "", text)

    # Remove substrings starting with "Source" and ending with "]"
    text = re.sub(r"Source[^\]]*?\]", "", text)

    return text
