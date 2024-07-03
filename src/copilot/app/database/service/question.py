from sqlalchemy.orm import Session

from .base import CRUDBase
from .document import crud_document
from ..models import Question, Document
from ..schemas import QuestionCreate, QuestionsCreate, DocumentCreate


class CRUDQuestion(CRUDBase):
    def __init__(self):
        super().__init__(Question)

    def create(self, db: Session, question: QuestionCreate):
        document_db = DocumentCreate(language=question.language, text=question.answer, url=question.url, source_id=question.source_id)
        answer = crud_document.create(db, document_db)
        db_question = Question(**question.model_dump(), answer_id=answer.id)
        return super().create(db, db_question)

    def create_all(self, db: Session, obj_in: QuestionsCreate):
        db_obj = []
        for obj in obj_in.questions:
            document_db = DocumentCreate(language=obj.language, text=obj.answer, url=obj.url, source_id=obj.source_id)
            answer = crud_document.create(db, document_db)
            db_question = Question(**obj.model_dump(), answer_id=answer.id)
            db_obj.append(db_question)
        return super().create_all(db, db_obj)

    def get_by_question(self, db: Session, question: str):
        test = db.query(self.model)
        test = test.filter(self.model.question == question)
        return test.first()

    def create_or_update(self, db: Session, question: QuestionCreate):
        db_question = self.get_by_question(db, question.question)
        if db_question:
            return self.update(db, db_question, question)
        else:
            return self.create(db, question)


crud_question_faq = CRUDQuestion()
