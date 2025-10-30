from typing import Annotated, Literal, Sequence

from pydantic import BaseModel, Field, computed_field


type Sort = tuple[str, Literal['asc', 'desc']]


class PaginationParams(BaseModel):
    page: Annotated[int, Field(ge=0)] = 0
    size: Annotated[int, Field(gt=0, le=100)] = 100
    sort: Annotated[Sequence[Sort] | None, Field(None)] = None
