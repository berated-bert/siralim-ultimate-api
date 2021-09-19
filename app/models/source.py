from datetime import datetime

from typing import Optional
from pydantic import BaseModel

from .base import BaseModelOrm


class SourceModel(BaseModel, BaseModelOrm):
    id: int
    name: str
    slug: str
    description: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
