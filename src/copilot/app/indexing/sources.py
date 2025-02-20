from tiktoken.core import Encoding
from sqlalchemy.orm import Session

from chat.messages import MessageBuilder
from llm.base import BaseLLM
from config.base_config import rag_config
from database.models import Source
from database.service import document_service
from utils.logging import get_logger

logger = get_logger(__name__)


async def create_source_descriptions(
    db: Session,
    message_builder: MessageBuilder,
    llm_client: BaseLLM,
    tokenizer: Encoding,
) -> None:
    """
    Create source descriptions for all sources in the database.
    Only generates descriptions for sources where description field is null.
    """
    # TO DO: tokenizer factory for all llm models
    # enums for model params (eg. max tokens)
    # subtract prompt length from max tokens
    # language management in doc preprocessing
    try:
        # Get only sources with null descriptions
        sources = db.query(Source).filter(Source.description.is_(None)).all()
        logger.info(f"Found {len(sources)} sources without descriptions")

        # Get all documents grouped by source
        for source in sources:
            documents = document_service.get_all_documents(
                db, source=[source.url]
            )
            if not documents:
                logger.warning(f"No documents found for source: {source.url}")
                continue

            combined_text = "\n\n".join([doc.text for doc in documents])
            language = documents[0].language

            logger.info(
                f"Processing source URL: {source.url} with {len(documents)} documents"
            )

            # Generate source description
            n_tokens = len(tokenizer.encode(combined_text))
            if n_tokens > 128_000:
                logger.warning(
                    f"Too many documents for '{source.url}': ({n_tokens} tokens). Truncated to max token input."
                )
                combined_text = tokenizer.decode(
                    tokenizer.encode(combined_text)[:125_000]
                )

            messages = message_builder.build_source_description_prompt(
                language=language,
                llm_model=rag_config["llm"]["model"],
                source_name=source.url,
                docs=combined_text,
            )
            llm_description = await llm_client.chat.completions.create(
                model=rag_config["llm"]["model"],
                stream=False,
                temperature=0,
                top_p=0.95,
                max_tokens=2048,
                messages=messages,
            )

            # Update source description in database
            description = (
                (
                    "**USER UPLOADED DOCUMENT:** "
                    + llm_description.choices[0].message.content
                )
                if source.url.startswith("user_pdf_upload")
                else llm_description.choices[0].message.content
            )
            source.description = description
            db.commit()

            logger.info(f"Updated source description for {source.url}")

    finally:
        db.close()
