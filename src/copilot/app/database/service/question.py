from sqlalchemy import select
from sqlalchemy.orm import Session

from .matching import MatchingService
from .document import document_service
from .source import source_service
from ..models import Question, Document, Source
from ..schemas import QuestionCreate, QuestionsCreate, DocumentCreate, SourceCreate

from utils.embedding import get_embedding

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QuestionService(MatchingService):
    def __init__(self):
        super().__init__(Question)

    def _create(self, db: Session, obj_in: QuestionCreate, source: Source = None):
        db_document = document_service.upsert(db, DocumentCreate(url=obj_in.url, text=obj_in.answer, language=obj_in.language, source=obj_in.source))

        db_question = Question(text=obj_in.text, answer=db_document, answer_id=db_document.id, language=obj_in.language, url=obj_in.url, source=db_document.source, source_id=db_document.source_id)
        db.add(db_question)

        return db_question

    def create_all(self, db: Session, objs_in: QuestionsCreate):
        db_source = source_service.get_or_create(db, Source(url=objs_in.source))

        db_objs = []
        for obj_in in objs_in.objects:
            db_objs.append(self._create(db, obj_in, db_source))
        db.commit()
        return db_objs

    def upsert(self, db: Session, obj_in: QuestionCreate):
        db_question = self.get_by_text(db, obj_in.text)
        if db_question:
            return self.update(db, db_question, obj_in)
        else:
            db_question = self.create(db, obj_in)
            return db_question

    def upsert_all(self, db: Session, obj_in: QuestionsCreate):
        db_questions = []
        for obj_in in obj_in.objects:
            db_questions.append(self.upsert(db, obj_in))
        db.commit()
        return db_questions

    def get_by_text(self, db: Session, question: str):
        return db.query(self.model).filter(self.model.text == question).one_or_none()

    def _update(self, db: Session, db_question: Question, question: QuestionCreate):
        document_service.update(db, db_question.answer, DocumentCreate(url=question.url, text=question.answer, language=question.language, source=question.source))

        db_question.text = question.text
        db_question.answer.text = question.answer
        db_question.language = question.language
        db_question.url = question.url
        db_question.source.url = question.source
        return db_question

    def _embed(self, db_question: Question):
        db_question.embedding = get_embedding(db_question.text)[0].embedding
        return db_question

    def embed(self, db: Session, db_question: Question):
        db_question = self._embed(db_question)
        db.commit()
        return db_question

    def embed_all(self, db: Session):
        questions = db.scalars(select(self.model)).all()
        for question in questions:
            self._embed(question)
        db.commit()
        return questions

    def embed_empty(self, db: Session):
        questions = db.scalars(select(self.model).filter(self.model.embedding.is_(None))).all()
        for question in questions:
            self._embed(question)
        db.commit()
        return questions

    def save(self, db: Session, question: QuestionCreate):
        db_question = self.get_by_text(db, question.text)
        if db_question:
            db_question = self._update(db, db_question, question)
        else:
            db_question = self._create(db, question)

        db.commit()
        return db_question


question_service = QuestionService()
