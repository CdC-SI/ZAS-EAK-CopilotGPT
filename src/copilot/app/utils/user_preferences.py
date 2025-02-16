from sqlalchemy.orm import Session
from redis import Redis, RedisError

from schemas.agents import UserPreferences as UserPreferencesSchema
from database.models import UserPreferences
from memory.config import RedisConfig
from .logging import get_logger

logger = get_logger(__name__)

# Initialize Redis client
redis_config = RedisConfig()
redis_client = Redis(
    host=redis_config.host,
    port=redis_config.port,
    db=redis_config.db,
    password=redis_config.password,
    decode_responses=redis_config.decode_responses,
)


def update_user_preferences_in_db(
    db: Session,
    user_uuid: str,
    user_preferences: UserPreferencesSchema,
) -> str:
    """Helper function to update user preferences in database and Redis cache."""
    # Convert to dict for storage
    preferences_dict = {
        "communication_preferences": user_preferences.communication_preferences.dict(),
        "interaction_preferences": user_preferences.interaction_preferences.dict(),
        "learning_style": user_preferences.learning_style.dict(),
        "historical_behaviour": user_preferences.historical_behaviour.dict(),
        "contextual_preferences": user_preferences.contextual_preferences.dict(),
    }

    try:
        # Update Redis cache first
        redis_key = f"user_preferences:{user_uuid}"
        redis_client.hset(redis_key, mapping=preferences_dict)
        # Set TTL for cached preferences (2 weeks))
        # redis_client.expire(redis_key, 1209600)
    except RedisError as e:
        logger.error(
            f"Failed to update Redis cache for user {user_uuid}: {str(e)}"
        )
        # Continue with DB update even if Redis fails

    # Update PostgreSQL
    existing_prefs = (
        db.query(UserPreferences)
        .filter(UserPreferences.user_uuid == user_uuid)
        .first()
    )

    if existing_prefs:
        existing_prefs.user_preferences = preferences_dict
        db.merge(existing_prefs)
    else:
        new_prefs = UserPreferences(
            user_uuid=user_uuid, user_preferences=preferences_dict
        )
        db.add(new_prefs)

    try:
        db.commit()
        return user_preferences.confirmation_msg
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update user preferences: {str(e)}")
        return "Failed to update user preferences. Please try again later"
