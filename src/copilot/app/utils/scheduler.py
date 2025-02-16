import tiktoken

from utils.logging import get_logger
from database.service.document import document_service
from database.service.source import source_service
from database.database import get_db
from indexing.sources import create_source_descriptions
from chat.messages import MessageBuilder
from memory.config import MemoryConfig
from memory import MemoryService
from agents.user_preferences import update_user_preferences
from config.clients_config import config
from config.base_config import rag_config, chat_config

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()

message_builder = MessageBuilder()
llm_client = config.factory.create_llm_client(rag_config["llm"]["model"])
memory_config = MemoryConfig.from_dict(chat_config["memory"])
memory_service = MemoryService(
    memory_type=memory_config.memory_type,
    k_memory=memory_config.k_memory,
    config=memory_config.storage,
)
tokenizer = tiktoken.encoding_for_model(rag_config["llm"]["model"])


def run_async_job(func):
    """Helper function to run async jobs in scheduler"""

    async def wrapper():
        try:
            await func()
        except Exception as e:
            logger.error(f"Error in scheduled job: {e}")

    return wrapper


# Define lifespan as a method
async def start_scheduler():
    """Initialize the scheduler with jobs"""
    if not scheduler.running:
        # Schedule document cleanup
        scheduler.add_job(
            func=lambda: document_service.delete_expired_documents(
                next(get_db())
            ),
            trigger=CronTrigger(hour=0, minute=0),
            id="delete_expired_documents",
            replace_existing=True,
        )

        # Schedule source descriptions update with async wrapper
        scheduler.add_job(
            func=lambda: create_source_descriptions(
                next(get_db()), message_builder, llm_client, tokenizer
            ),
            trigger=CronTrigger(
                hour="0,7,8,9,19,11,12,13,14,15,16,17,18", minute=0
            ),
            id="create_source_descriptions",
            replace_existing=True,
        )

        # Schedule source cleanup
        scheduler.add_job(
            func=lambda: source_service.delete_expired_sources(next(get_db())),
            trigger=CronTrigger(hour=1, minute=0),
            id="delete_expired_sources",
            replace_existing=True,
        )

        # Schedule user preferences update
        scheduler.add_job(
            func=run_async_job(
                lambda: update_user_preferences(
                    db=next(get_db()),
                    memory_service=memory_service,
                    message_builder=message_builder,
                    llm_client=llm_client,
                    tokenizer=tokenizer,
                )
            ),
            trigger=CronTrigger(day="*/14", hour=23, minute=0),
            id="update_user_preferences",
            replace_existing=True,
        )

        scheduler.start()
        logger.info("Scheduler started.")


async def stop_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown completed.")
