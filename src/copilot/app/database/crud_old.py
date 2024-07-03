from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, schemas
from utils.embedding import get_embedding


def get_exact_match(db: Session, user_input: str, language: str = None, k: int = 0):
    """
    Get exact match from database

    Parameters
    ----------
    db : Session
    user_input : str
        User input to match database entries
    language : str, optional
        Question and results language
    k : int, optional
        Number of results to return

    Returns
    -------
    list of dict
    """
    search = "%{}%".format(user_input)

    results = db.query(models.ArticleFAQ)
    if language:
        results = results.filter(models.ArticleFAQ.language == language)

    results = results.filter(models.ArticleFAQ.question.like(search))
    if k > 0:
        results = results.limit(k)

    return results.all()


def get_fuzzy_match(db: Session, user_input: str, threshold: int = 150, language: str = None, k: int = 0):
    """
    Get fuzzy match from database

    Parameters
    ----------
    db : Session
    user_input : str
        User input to match database entries
    threshold : int, optional
    language : str, optional
        Question and results language
    k : int, optional
        Number of results to return

    Returns
    -------
    list of dict
    """
    results = db.query(models.ArticleFAQ)
    if language:
        results = results.filter(models.ArticleFAQ.language == language)

    results = (results
               .filter(func.levenshtein_less_equal(models.ArticleFAQ.question, user_input, threshold) < threshold)
               .order_by(func.levenshtein(models.ArticleFAQ.question, user_input).asc()))

    if k > 0:
        results = results.limit(k)

    return results.all()


def get_trigram_match(db: Session, user_input: str, threshold: int = 0.5, language: str = None, k: int = 0):
    """
    Get trigram match from database

    Parameters
    ----------
    db : Session
    user_input : str
        User input to match database entries
    threshold : int, optional
    language : str, optional
        Question and results language
    k : int, optional
        Number of results to return

    Returns
    -------
    list of dict
    """
    results = db.query(models.ArticleFAQ)
    if language:
        results = results.filter(models.ArticleFAQ.language == language)

    results = (results
               .filter(func.word_similarity(user_input, models.ArticleFAQ.question) > threshold)
               .order_by(func.word_similarity(user_input, models.ArticleFAQ.question).desc()))
    if k > 0:
        results = results.limit(k)

    return results.all()


def get_semantic_match(db: Session, user_input: str, symbol: str = '<=>', language: str = None, k: int = 0):
    """
    Get semantic match from database

    Parameters
    ----------
    db : Session
    user_input : str
        User input to match database entries
    symbol : str, optional
    language : str, optional
    k : int, optional

    Returns
    -------
    list of dict
    """
    q_embedding = get_embedding(user_input)[0].embedding

    results = db.query(models.Document)
    if language:
        results = results.filter(models.Document.language == language)

    results = results.order_by(func.op(symbol)(q_embedding).asc())
    if k > 0:
        results = results.limit(k)

    return results.all()


def semantic_similarity_match_l1(db: Session, user_input: str, language: str = None, k: int = 0):
    return get_semantic_match(db, user_input, symbol='<+>', language=language, k=k)


def semantic_similarity_match_l2(db: Session, user_input: str, language: str = None, k: int = 0):
    return get_semantic_match(db, user_input, symbol='<->', language=language, k=k)


def semantic_similarity_match_inner_prod(db: Session, user_input: str, language: str = None, k: int = 0):
    return get_semantic_match(db, user_input, symbol='<#>', language=language, k=k)


def add_article_faq_item(db: Session, article: schemas.ArticleFAQCreate, source_id: int):
    db_article = models.ArticleFAQ(**article.dict(), source_id=source_id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def add_document_item(db: Session, document: schemas.DocumentCreate, source_id: int):
    db_document = models.Document(**document.dict(), source_id=source_id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def add_or_update_article_faq(db: Session, article: schemas.ArticleFAQCreate, source_id: int):
    db_article = db.query(models.ArticleFAQ).filter(models.ArticleFAQ.question == article.question).first()
    if db_article:
        db_article.answer = db_article.answer
        db.commit()
        db.refresh(db_article)
        return db_article
    else:
        return add_article_faq_item(db, article, source_id)
