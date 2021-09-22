from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func

from app.orm.status_effect import StatusEffectOrm
from app.models.status_effect import StatusEffectModel
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
    prefix="/status-effects",
    tags=["status-effects"],
)

SORTING_FILTER_FIELDS = [
    StatusEffectOrm.id,
    StatusEffectOrm.name,
    StatusEffectOrm.category,
    StatusEffectOrm.turns,
    StatusEffectOrm.leave_chance,
    StatusEffectOrm.max_stacks,
]

SortingSchema = build_sorting_schema(SORTING_FILTER_FIELDS)


class IndexSchema(BaseModel):
    data: List[StatusEffectModel]
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
    status_effects_count = select(
        func.count(StatusEffectOrm.id.distinct())
    ).get_scalar(session)
    status_effects_orm = (
        select(StatusEffectOrm)
        .pagination(pagination)
        .sorting(sorting)
        .get_scalars(session)
    )
    status_effects_model = StatusEffectModel.from_orm_list(status_effects_orm)
    return IndexSchema(
        data=status_effects_model,
        pagination=PaginationResponseSchema.from_request(
            pagination, status_effects_count
        ),
        sorting=sorting,
    )


FilterSchema = build_filtering_schema(SORTING_FILTER_FIELDS)


class SearchSchema(BaseModel):
    data: List[StatusEffectModel]
    filter: FilterSchema
    pagination: PaginationRequestSchema
    sorting: SortingSchema


class SearchRequest(BaseModel):
    filter: FilterSchema
    pagination: Optional[PaginationRequestSchema] = PaginationRequestSchema()
    sorting: Optional[SortingSchema] = SortingSchema()


@router.post("/search", response_model=SearchSchema)
def search(search: SearchRequest, session=Depends(has_session)):
    status_effects_count = (
        select(func.count(StatusEffectOrm.id.distinct()))
        .filters(search.filter.filters)
        .get_scalar(session)
    )
    status_effects_orm = (
        select(StatusEffectOrm)
        .filters(search.filter.filters)
        .pagination(search.pagination)
        .sorting(search.sorting)
        .get_scalars(session)
    )
    status_effects_model = StatusEffectModel.from_orm_list(status_effects_orm)
    return SearchSchema(
        data=status_effects_model,
        filter=search.filter,
        pagination=PaginationResponseSchema.from_request(
            search.pagination, status_effects_count
        ),
        sorting=search.sorting,
    )


class GetSchema(BaseModel):
    data: StatusEffectModel


@router.get("/{status_effect_id}", response_model=GetSchema)
def get(status_effect_id: str, session=Depends(has_session)):
    status_effect_orm = (
        select(StatusEffectOrm)
        .where(StatusEffectOrm.where_slug_or_id(status_effect_id))
        .get_scalar(session)
    )
    status_effect_model = StatusEffectModel.from_orm(status_effect_orm)
    return GetSchema(data=status_effect_model)
