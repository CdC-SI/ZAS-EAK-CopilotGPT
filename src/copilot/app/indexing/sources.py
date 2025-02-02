import tiktoken

from database.database import SessionLocal
from chat.messages import MessageBuilder
from config.base_config import rag_config
from config.clients_config import config
from database.models import Source
from database.service import document_service
from utils.logging import get_logger

logger = get_logger(__name__)


async def create_source_descriptions() -> None:
    """
    Create source descriptions for all sources in the database.
    Only generates descriptions for sources where description field is null.
    """
    # TO DO: tokenizer factory for all llm models
    # enums for model params (eg. max tokens)
    # subtract prompt length from max tokens
    # language management in doc preprocessing

    db = SessionLocal()
    message_builder = MessageBuilder()
    llm_client = config.factory.create_llm_client(rag_config["llm"]["model"])
    tokenizer = tiktoken.encoding_for_model(rag_config["llm"]["model"])

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
            source_description = await llm_client.chat.completions.create(
                model=rag_config["llm"]["model"],
                stream=False,
                temperature=0,
                top_p=0.95,
                max_tokens=2048,
                messages=messages,
            )

            # Update source description in database
            source.description = source_description.choices[0].message.content
            db.commit()

            logger.info(f"Updated source description for {source.url}")

    finally:
        db.close()
