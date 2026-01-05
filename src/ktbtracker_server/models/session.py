from typing import Annotated, Any

from pydantic import BaseModel, Field


class SessionData(BaseModel):
    # Standard JWT Claims
    issuer: Annotated[str | None, Field(alias="iss")] = None
    audience: Annotated[str | None, Field(alias="aud")] = None
    subject: Annotated[str | None, Field(alias="sub")] = None
    issued_at: Annotated[int | None, Field(alias="iat")] = None
    expires_at: Annotated[int | None, Field(alias="exp")] = None

    # Custom Claims
    name: Annotated[str | None, Field(alias="name")] = None
    email: Annotated[str | None, Field(alias="email")] = None
    email_verified: Annotated[bool | None, Field(alias="email_verified")] = None
    user_id: Annotated[str | None, Field(alias="user_id")] = None
    auth_time: Annotated[int | None, Field(alias="auth_time")] = None
    firebase: Annotated[dict[str, Any] | None, Field(alias="firebase")] = None

    # Query Defaults
    candidate_id: Annotated[int | None, Field(alias="candidate_id")] = None
    tracking_date: Annotated[str | None, Field(alias="tracking_date")] = None
    week: Annotated[int | None, Field(alias="week")] = None
