from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from database.models import ChatHistory, ChatTitle
from ..interfaces.storage import DatabaseStorage
from ..exceptions import PostgresStorageError
from ..models import MessageData
from ..enums import MessageRole


class PostgresMemoryHandler(DatabaseStorage):
    def index_chat_history(self, db: Session, message: MessageData) -> None:
        # Convert MessageRole enum to string value
        role = (
            message.role.value
            if isinstance(message.role, MessageRole)
            else message.role
        )

        chat_history = ChatHistory(
            user_uuid=message.user_uuid,
            conversation_uuid=message.conversation_uuid,
            message_uuid=message.message_uuid,
            role=role,
            message=message.message,
            url=message.url,
            language=message.language,
            faq_id=message.faq_id,
            retrieved_docs=message.retrieved_doc_ids,
            timestamp=message.timestamp,
        )
        try:
            db.add(chat_history)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise PostgresStorageError(f"Failed to index chat history: {e}")

    def conversation_uuid_exists(
        self, db: Session, conversation_uuid: str
    ) -> bool:
        result = db.execute(
            select(ChatTitle).filter_by(conversation_uuid=conversation_uuid)
        )
        return result.scalars().first() is not None

    def index_chat_title(
        self, db: Session, user_uuid: str, conversation_uuid: str, title: str
    ) -> None:
        chat_title = ChatTitle(
            user_uuid=user_uuid,
            conversation_uuid=conversation_uuid,
            chat_title=title,
        )
        try:
            db.add(chat_title)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise PostgresStorageError(f"Failed to index chat title: {e}")
