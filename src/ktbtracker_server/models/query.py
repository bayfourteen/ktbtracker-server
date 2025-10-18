from typing import Annotated

from pydantic import BaseModel, Field, computed_field


class PaginationParams(BaseModel):
    page: Annotated[int, Field(ge=0)] = 0
    size: Annotated[int, Field(gt=0, le=100)] = 100
    sort: Annotated[list[str] | None, Field(None)] = None
