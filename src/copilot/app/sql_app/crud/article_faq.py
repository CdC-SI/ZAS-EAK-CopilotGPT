from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models import ArticleFAQ
from ..schemas import *


class CRUDArticleFAQ(CRUDBase):
    def __init__(self):
        super().__init__(ArticleFAQ)

    def get_by_question(self, db: Session, question: str):
        return db.query(self.model).filter(self.model.question == question).first()

    def add_or_update(self, db: Session, article: ArticleFAQCreate):
        db_article = self.get_by_question(db, article.question)
        if db_article:
            return self.update(db, db_article, article)
        else:
            return self.add(db, article)


crud_article_faq = CRUDArticleFAQ()
