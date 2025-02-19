from memory.enums import MessageRole
import ast
import re
from typing import Dict

from schemas.chat import ChatRequest
from chat.messages import MessageBuilder
from llm.base import BaseLLM
from schemas.agents import ParseTranslateArgs

from langfuse.decorators import observe


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


@observe(name="parse_translation_args")
async def parse_translation_args(
    request: ChatRequest,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
) -> Dict[str, str]:
    """
    Parse user query with LLM to extract args for translation.
    """
    messages = message_builder.build_parse_translate_args_prompt(
        request.language,
        request.llm_model,
        request.query,
    )

    res = await llm_client.llm_client.beta.chat.completions.parse(
        model="gpt-4o",
        temperature=0,
        top_p=0.95,
        max_tokens=4096,
        messages=messages,
        response_format=ParseTranslateArgs,
    )

    arg_names = ["target_lang", "n_msg", "roles"]
    arg_values = res.choices[0].message.parsed.arg_values

    parsed_args = []
    for arg in arg_values:
        try:
            parsed_value = ast.literal_eval(arg)
        except (ValueError, SyntaxError):
            # Handle MessageRole enum values
            if arg.startswith("[MessageRole.") and arg.endswith("]"):
                enum_values = arg.strip("[]").split(",")
                parsed_value = [
                    getattr(MessageRole, enum_val.split(".")[-1].strip())
                    for enum_val in enum_values
                ]
            else:
                parsed_value = arg

        parsed_args.append(parsed_value)

    args = {name: value for name, value in zip(arg_names, parsed_args)}

    return args
