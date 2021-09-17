from sqlalchemy import Column, Integer, String, Text, Enum
from .base import BaseOrm, build_slug_defaulter
from app.common.status_effect import StatusEffectCategoriesEnum

class StatusEffectOrm(BaseOrm):
  __tablename__ = "status_effects"

  slug_defaulter = build_slug_defaulter("name")

  id = Column(Integer, primary_key=True)
  name = Column(String(50), nullable=False)
  slug = Column(String(50), nullable=False, unique=True, default=slug_defaulter, onupdate=slug_defaulter)
  description = Column(Text())

  category = Column(Enum(StatusEffectCategoriesEnum))

  icon = Column(Text(), nullable=False)

  turns = Column('turns')
  leave_chance = Column('leave_chance', Integer)
  max_stacks = Column('max_stacks', Integer, nullable=False)