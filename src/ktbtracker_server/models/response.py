from typing import TypeVar, Generic, Sequence, Annotated, Mapping, Any, List

from fastapi import Request
from pydantic import BaseModel, computed_field, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class Link(BaseModel):
    href: str
    rel: str
    # method: Annotated[str | None, Field(exclude_if=lambda v: v is None)] = None


class CollectionResponse(BaseModel, Generic[T]):
    content: Sequence[T]


class Pagination(BaseModel, alias_generator=to_camel, populate_by_name=True):
    page: int
    page_size: int
    total_elements: int

    @computed_field
    @property
    def total_pages(self) -> int:
        return int((self.total_elements // self.page_size) + int((self.total_elements % self.page_size) > 0)) \
            if self.page_size else 0


class PagedResponse(BaseModel, Generic[T]):
    pagination: Pagination
    content: Sequence[T]
    links: Annotated[Mapping[str, Any] | None, Field(alias='links', exclude=False)] = None

    def with_links(self, request: Request) -> 'PagedResponse[T]':
        first_page = 0
        last_page = self.pagination.total_pages - 1 if self.pagination.total_pages > 0 else first_page
        curr_page = last_page if self.pagination.page > last_page else first_page \
            if self.pagination.page < first_page else first_page
        next_page = curr_page + 1 if curr_page < last_page else last_page
        prev_page = curr_page - 1 if curr_page > first_page else first_page

        self.links = dict(
            self=dict(href=str(request.url.include_query_params(page=curr_page, size=self.pagination.page_size))),
            first=dict(href=str(request.url.include_query_params(page=first_page, size=self.pagination.page_size))),
            last=dict(href=str(request.url.include_query_params(page=last_page, size=self.pagination.page_size))),
            next=dict(href=str(request.url.include_query_params(page=next_page, size=self.pagination.page_size))),
            prev=dict(href=str(request.url.include_query_params(page=prev_page, size=self.pagination.page_size))),
        )

        return self
