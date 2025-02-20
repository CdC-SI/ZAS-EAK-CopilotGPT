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
        """
        Store chat message in database.

        Parameters
        ----------
        db : Session
            SQLAlchemy database session
        message : MessageData
            Message data to be stored

        Raises
        ------
        PostgresStorageError
            If database operation fails
        """
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
            sources=message.sources,
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
        """
        Check if conversation exists in database.

        Parameters
        ----------
        db : Session
            SQLAlchemy database session
        conversation_uuid : str
            UUID of conversation to check

        Returns
        -------
        bool
            True if conversation exists, False otherwise
        """
        result = db.execute(
            select(ChatTitle).filter_by(conversation_uuid=conversation_uuid)
        )
        return result.scalars().first() is not None

    def index_chat_title(
        self, db: Session, user_uuid: str, conversation_uuid: str, title: str
    ) -> None:
        """
        Store chat title in database.

        Parameters
        ----------
        db : Session
            SQLAlchemy database session
        user_uuid : str
            UUID of user
        conversation_uuid : str
            UUID of conversation
        title : str
            Title of chat

        Raises
        ------
        PostgresStorageError
            If database operation fails
        """
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

    def get_conversation_history(
        self, db: Session, user_uuid: str, conversation_uuid: str
    ) -> list[MessageData]:
        """
        Retrieve conversation history for specific user and conversation.

        Parameters
        ----------
        db : Session
            SQLAlchemy database session
        user_uuid : str
            UUID of user
        conversation_uuid : str
            UUID of conversation

        Returns
        -------
        list[MessageData]
            List of messages in conversation

        Raises
        ------
        PostgresStorageError
            If database query fails
        """
        try:
            result = db.execute(
                select(ChatHistory)
                .filter_by(
                    user_uuid=user_uuid, conversation_uuid=conversation_uuid
                )
                .order_by(ChatHistory.timestamp)
            )
            chat_history = result.scalars().all()

            return [
                MessageData(
                    user_uuid=msg.user_uuid,
                    conversation_uuid=msg.conversation_uuid,
                    message_uuid=msg.message_uuid,
                    role=msg.role,
                    message=msg.message,
                    sources=msg.sources,
                    language=msg.language,
                    faq_id=msg.faq_id,
                    retrieved_doc_ids=msg.retrieved_docs,
                    timestamp=msg.timestamp,
                )
                for msg in chat_history
            ]
        except SQLAlchemyError as e:
            raise PostgresStorageError(f"Failed to retrieve chat history: {e}")

    def get_all_user_conversations(
        self, db: Session, user_uuid: str
    ) -> list[MessageData]:
        """
        Retrieve all conversations for a given user.

        Parameters
        ----------
        db : Session
            SQLAlchemy database session
        user_uuid : str
            UUID of the user

        Returns
        -------
        list[MessageData]
            List of all messages from user's conversations

        Raises
        ------
        PostgresStorageError
            If database query fails
        """
        try:
            result = db.execute(
                select(ChatHistory)
                .filter_by(user_uuid=user_uuid)
                .order_by(ChatHistory.conversation_uuid, ChatHistory.timestamp)
            )
            chat_history = result.scalars().all()

            return [
                MessageData(
                    user_uuid=msg.user_uuid,
                    conversation_uuid=msg.conversation_uuid,
                    message_uuid=msg.message_uuid,
                    role=msg.role,
                    message=msg.message,
                    sources=msg.sources,
                    language=msg.language,
                    faq_id=msg.faq_id,
                    retrieved_doc_ids=msg.retrieved_docs,
                    timestamp=msg.timestamp,
                )
                for msg in chat_history
            ]
        except SQLAlchemyError as e:
            raise PostgresStorageError(
                f"Failed to retrieve user conversations: {e}"
            )
