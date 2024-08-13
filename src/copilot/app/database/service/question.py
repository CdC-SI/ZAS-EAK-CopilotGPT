from typing import Union, Tuple

from sqlalchemy.orm import Session

from .matching import MatchingService
from .document import document_service
from ..models import Question
from schemas.question import QuestionCreate, QuestionUpdate
from schemas.document import DocumentCreate

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QuestionService(MatchingService):
    """
    Class that provide services for question database operations
    """
    def __init__(self):
        super().__init__(Question)

    def _create(self, db: Session, obj_in: QuestionCreate, embed: Union[Tuple[bool, bool], bool] = False):
        # if embed is not a tuple, convert it to a tuple to use it for both question and answer
        if not isinstance(embed, tuple):
            embed = (embed, embed)

        # create the answer in documents first
        db_document = document_service.upsert(db, DocumentCreate(**obj_in.model_dump(exclude={"text", "answer","embedding"}), text=obj_in.answer), embed=embed[1])

        # create the question
        db_question = Question(text=obj_in.text, embedding=obj_in.embedding, answer=db_document, answer_id=db_document.id, language=obj_in.language, url=obj_in.url, source=db_document.source, source_id=db_document.source_id)
        if embed[0]:
            db_question = self._embed(db_question)

        db.add(db_question)

        return db_question

    def create(self, db: Session, obj_in: QuestionCreate, embed: Union[Tuple[bool, bool], bool] = False):
        """
        Create a new question object in the database

        Parameters
        ----------
        db: Session
            Database session
        obj_in: QuestionCreate
            Pydantic schema
        embed: Tuple[bool, bool], optional
            Whether question and/or answer should be embedded

        Returns
        -------

        """
        db_question = self._create(db, obj_in, embed=embed)
        db.commit()
        return db_question

    def _update(self, db: Session, db_question: Question, question: QuestionCreate, embed: Union[Tuple[bool, bool], bool] = False):
        # if embed is not a tuple, convert it to a tuple to use it for both question and answer
        if not isinstance(embed, tuple):
            embed = (embed, embed)

        # update the answer in documents first
        document_service.update(db, db_question.answer, DocumentCreate(url=question.url, text=question.answer, language=question.language, source=question.source), embed=embed[1])

        # update the question
        exclude = self._update_embed_exclude(db_question, question, embed[0])
        super()._update(db, db_question, QuestionUpdate(**question.model_dump(exclude=exclude), source_id=db_question.answer.source_id))

        return db_question


question_service = QuestionService()
