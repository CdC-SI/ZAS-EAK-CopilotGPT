from .base import CRUDBase
from ..models import ArticleFAQ


class CRUDDocument(CRUDBase):
    def __init__(self):
        super().__init__(ArticleFAQ)


crud_document = CRUDDocument()
