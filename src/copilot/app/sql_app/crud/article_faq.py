from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models import ArticleFAQ
from ..schemas import ArticleFAQCreate, ArticlesFAQCreate


class CRUDArticleFAQ(CRUDBase):
    def __init__(self):
        super().__init__(ArticleFAQ)

    def create(self, db: Session, article: ArticleFAQCreate):
        db_article = ArticleFAQ(**article.dict())
        return super().create(db, db_article)

    def create_all(self, db: Session, obj_in: ArticlesFAQCreate):
        db_obj = [ArticleFAQ(**obj.dict()) for obj in obj_in.articles]
        return super().create(db, db_obj)

    def get_by_question(self, db: Session, question: str):
        test = db.query(self.model)
        test = test.filter(self.model.question == question)
        return test.first()

    def create_or_update(self, db: Session, article: ArticleFAQCreate):
        db_article = self.get_by_question(db, article.question)
        if db_article:
            return self.update(db, db_article, article)
        else:
            return self.create(db, article)


crud_article_faq = CRUDArticleFAQ()
