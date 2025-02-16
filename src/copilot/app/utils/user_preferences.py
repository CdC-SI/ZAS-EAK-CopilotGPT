from sqlalchemy.orm import Session

from schemas.agents import UserPreferences as UserPreferencesSchema
from database.models import UserPreferences
from .logging import get_logger

logger = get_logger(__name__)


def update_user_preferences_in_db(
    db: Session,
    user_uuid: str,
    user_preferences: UserPreferencesSchema,
) -> str:
    """Helper function to update user preferences in the database."""
    # Convert to dict for DB storage
    preferences_dict = {
        "communication_preferences": user_preferences.communication_preferences.dict(),
        "interaction_preferences": user_preferences.interaction_preferences.dict(),
        "learning_style": user_preferences.learning_style.dict(),
        "historical_behaviour": user_preferences.historical_behaviour.dict(),
        "contextual_preferences": user_preferences.contextual_preferences.dict(),
    }

    # TO DO: store in redis cache
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
