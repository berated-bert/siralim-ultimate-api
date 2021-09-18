from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.orm.spell import SpellOrm
from app.models.spell import SpellModel
from app.orm.klass import KlassOrm
from app.orm.source import SourceOrm
from .helpers import (
    PaginationSchema,
    build_sorting_schema,
    build_filtering_schema,
    select,
    has_session,
    has_pagination,
    has_sorting,
)

router = APIRouter(
    prefix="/spells",
    tags=["spells"],
)

SortingSchema = build_sorting_schema(
    [
        SpellOrm.id,
        SpellOrm.name,
        SpellOrm.charges,
        SpellOrm.klass_id,
        SpellOrm.klass_name,
        SpellOrm.source_id,
        SpellOrm.source_name,
    ]
)

EAGER_LOAD_OPTIONS = [
    contains_eager(SpellOrm.klass),
    contains_eager(SpellOrm.source),
]


class IndexSchema(BaseModel):
    data: List[SpellModel]
    pagination: PaginationSchema
    sorting: SortingSchema


pagination_depend = has_pagination()
sorting_depend = has_sorting(SortingSchema, "id")


@router.get("/", response_model=IndexSchema)
def index(
    session=Depends(has_session),
    pagination: PaginationSchema = Depends(pagination_depend),
    sorting: SortingSchema = Depends(sorting_depend),
):
    spells_orm = (
        select(SpellOrm)
        .join(KlassOrm)
        .join(SourceOrm)
        .options(*EAGER_LOAD_OPTIONS)
        .pagination(pagination)
        .sorting(sorting)
        .get_scalars(session)
    )
    spells_model = SpellModel.from_orm_list(spells_orm)
    return IndexSchema(
        data=spells_model, pagination=pagination, sorting=sorting
    )


class GetSchema(BaseModel):
    data: SpellModel


@router.get("/{spell_id}", response_model=GetSchema)
def get(spell_id: str, session=Depends(has_session)):
    spell_orm = (
        select(SpellOrm)
        .join(KlassOrm)
        .join(SourceOrm)
        .options(*EAGER_LOAD_OPTIONS)
        .where(SpellOrm.where_slug_or_id(spell_id))
        .get_scalar(session)
    )
    spell_model = SpellModel.from_orm(spell_orm)
    return GetSchema(data=spell_model)
