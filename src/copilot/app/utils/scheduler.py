from utils.logging import get_logger
from database.service.document import document_service
from database.service.source import source_service
from database.database import get_db
from indexing.sources import create_source_descriptions

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


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
            func=run_async_job(create_source_descriptions),
            trigger=CronTrigger(hour="0,6,12,18", minute=0),
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

        scheduler.start()
        logger.info("Scheduler started.")


async def stop_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown completed.")
