from .base import CRUDBase
from ..models import Source


class CRUDSource(CRUDBase):
    def __init__(self):
        super().__init__(Source)


crud_source = CRUDSource()
