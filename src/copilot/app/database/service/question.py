from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_upsert

from .base import CRUDBase
from .document import crud_document
from ..models import Question, Document
from ..schemas import QuestionCreate, QuestionsCreate, DocumentCreate

from utils.embedding import get_embedding


class CRUDQuestion(CRUDBase):
    def __init__(self):
        super().__init__(Question)

    def create_all(self, db: Session, obj_in: QuestionsCreate):
        db_obj = []
        return super().create_all(db, db_obj)

    def upsert(self, db: Session, objs: list[dict]):
        stmt = pg_upsert(self.model).values(objs)
        stmt = stmt.on_conflict_do_update(
            index_elements=[self.model.text],
            set_={
                "answer": stmt.excluded.answer,
                "language": stmt.excluded.language,
                "url": stmt.excluded.url,
                "source_id": stmt.excluded.source_id
            }
        )

    def _create_or_update(self, db: Session, obj_in: QuestionCreate):
        db_question = crud_question.get_by_text(db, obj_in.text)
        if db_question:
            return self._update(db, db_question, obj_in)
        else:
            db_document = crud_document.get_by_text(db, obj_in.answer)
            if not db_document:
                document_in = DocumentCreate(language=obj_in.language, text=obj_in.answer, url=obj_in.url, source_id=obj_in.source_id)
                db_document = Document(url=document_in.url, language=document_in.language, text=document_in.text, source_id=document_in.source_id)
                db.add(db_document)
            db_question = Question(text=obj_in.text, answer_id=db_document.id, language=obj_in.language, url=obj_in.url, source_id=obj_in.source_id)
            db.add(db_question)
            return db_question

    def _create_or_update_all(self, db: Session, obj_in: QuestionsCreate):
        for question in obj_in.questions:
            self._create_or_update(db, question)

        db.commit()

        for question in obj_in.questions:
            db.refresh(question)
        return

    def get_by_text(self, db: Session, question: str):
        test = db.query(self.model)
        test = test.filter(self.model.text == question)
        return test.first()

    def _update(self, db: Session, db_question: Question, question: QuestionCreate):
        db_question.text = question.text
        db_question.answer.text = question.answer
        db_question.language = question.language
        db_question.url = question.url
        db_question.source.url = question.source_id
        return db_question

    def embed_all(self, db: Session):
        questions = db.query(self.model).filter(self.model.embedding.is_(None)).all()
        for question in questions:
            question.embedding = get_embedding(question.text)[0].embedding
        db.commit()
        db.refresh(question)
        return questions

    def create_or_update(self, db: Session, question: QuestionCreate):
        db_question = self.get_by_text(db, question.text)
        if db_question:
            return self.update(db, db_question, question)
        else:
            return self.create(db, question)


crud_question = CRUDQuestion()
