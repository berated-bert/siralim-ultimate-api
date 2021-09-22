from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.orm.spell import SpellOrm
from app.models.spell import SpellModel
from app.orm.klass import KlassOrm
from app.orm.source import SourceOrm
from .helpers import (
    PaginationRequestSchema,
    PaginationResponseSchema,
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

SORTING_FILTER_FIELDS = [
    SpellOrm.id,
    SpellOrm.name,
    SpellOrm.charges,
    SpellOrm.klass_id,
    SpellOrm.klass_name,
    SpellOrm.source_id,
    SpellOrm.source_name,
    SpellOrm.tags,
]

SortingSchema = build_sorting_schema(SORTING_FILTER_FIELDS)

EAGER_LOAD_OPTIONS = [
    contains_eager(SpellOrm.klass),
    contains_eager(SpellOrm.source),
]


class IndexSchema(BaseModel):
    data: List[SpellModel]
    pagination: PaginationRequestSchema
    sorting: SortingSchema


pagination_depend = has_pagination()
sorting_depend = has_sorting(SortingSchema)


@router.get("", response_model=IndexSchema, include_in_schema=False)
@router.get("/", response_model=IndexSchema)
def index(
    session=Depends(has_session),
    pagination: PaginationRequestSchema = Depends(pagination_depend),
    sorting: SortingSchema = Depends(sorting_depend),
):
    spells_count = select(func.count(SpellOrm.id.distinct())).get_scalar(
        session
    )
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
        data=spells_model,
        pagination=PaginationResponseSchema.from_request(
            pagination, spells_count
        ),
        sorting=sorting,
    )


FilterSchema = build_filtering_schema(SORTING_FILTER_FIELDS)


class SearchSchema(BaseModel):
    data: List[SpellModel]
    filter: FilterSchema
    pagination: PaginationRequestSchema
    sorting: SortingSchema


class SearchRequest(BaseModel):
    filter: FilterSchema
    pagination: Optional[PaginationRequestSchema] = PaginationRequestSchema()
    sorting: Optional[SortingSchema] = SortingSchema()


@router.post("/search", response_model=SearchSchema)
def search(search: SearchRequest, session=Depends(has_session)):
    spells_count = (
        select(func.count(SpellOrm.id.distinct()))
        .filters(search.filter.filters)
        .join(KlassOrm)
        .join(SourceOrm)
        .get_scalar(session)
    )
    spells_orm = (
        select(SpellOrm)
        .filters(search.filter.filters)
        .join(KlassOrm)
        .join(SourceOrm)
        .options(*EAGER_LOAD_OPTIONS)
        .pagination(search.pagination)
        .sorting(search.sorting)
        .get_scalars(session)
    )
    spells_model = SpellModel.from_orm_list(spells_orm)
    return SearchSchema(
        data=spells_model,
        filter=search.filter,
        pagination=PaginationResponseSchema.from_request(
            search.pagination, spells_count
        ),
        sorting=search.sorting,
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
