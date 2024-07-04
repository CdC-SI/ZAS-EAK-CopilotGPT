from sqlalchemy.orm import Session

from .base import CRUDBase
from .document import crud_document
from ..models import Question
from ..schemas import QuestionCreate, QuestionsCreate, DocumentCreate

from utils.embedding import get_embedding


class CRUDQuestion(CRUDBase):
    def __init__(self):
        super().__init__(Question)

    def create_all(self, db: Session, obj_in: QuestionsCreate):
        db_obj = []
        return super().create_all(db, db_obj)

    def _save(self, db: Session, obj_in: QuestionCreate):
        db_document = crud_document.get_by_text(db, obj_in.answer)
        if db_document:
            return self._update(db_document, obj_in)
        else:
            document_db = DocumentCreate(language=obj_in.language, text=obj_in.answer, url=obj_in.url, source_id=obj_in.source_id)
            answer = crud_document.create(db, document_db)
            db_question = Question(text=obj_in.text, answer_id=answer.id, language=obj_in.language, url=obj_in.url, source_id=obj_in.source_id)
            db.add(db_question)
            return db_question

    def save_all(self, db: Session, obj_in: QuestionsCreate):
        for question in obj_in.questions:
            self._save(db, question)

        db.commit()

        for question in obj_in.questions:
            db.refresh(question)
        return

    def get_by_text(self, db: Session, question: str):
        test = db.query(self.model)
        test = test.filter(self.model.text == question)
        return test.first()

    def _update(self, db: Session, db_question: Question, question: QuestionCreate):
        db_document = crud_document.get(db, db_question.answer_id)

        if db_document:
            db_document.text = question.answer
            db_document.language = question.language
            db_document.url = question.url
            db_document.source_id = question.source_id
        else:
            db_document = DocumentCreate(language=question.language, text=question.answer, url=question.url, source_id=question.source_id)

        db_question.text = question.text
        db_question.answer_id = db_document.id
        db_question.language = question.language
        db_question.url = question.url
        db_question.source_id = question.source_id
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
