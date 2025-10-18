from datetime import datetime, date, timezone
from typing import Optional, Annotated

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Index, Relationship
from sqlmodel import Column, TEXT


class SiteGroup(SQLModel, table=True):
    __tablename__ = 'usergroups'

    id: int = Field(primary_key=True)
    name: str
    description: str | None


class SiteUser(SQLModel, table=True):
    __tablename__ = 'users'

    id: int = Field(primary_key=True)
    user_id: str
    display_name: str
    email: str
    email_verified: bool = Field(default=False)
    photo_url: str | None

    candidates: list["Candidate"] = Relationship(back_populates="user")


class Metadata(SQLModel, arbitrary_types_allowed=True):
    created_by: int
    created: Annotated[datetime, Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
                                       default_factory=lambda: datetime.now(timezone.utc))]
    modified_by: int | None
    modified: Annotated[datetime | None, Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
                                               default_factory=lambda: datetime.now(timezone.utc))]


class Requirements(SQLModel):
    burpees: int
    class_dream_team: int
    class_hyper_pro: int
    class_master_q: int
    class_pmaa: int
    class_saturday: int
    class_sparring: int
    class_weekday: int
    journals: int
    jumps: float
    kicks: int
    leadership: int
    leadership2: int
    meditation: float
    mentee: int
    mentor: int
    miles: float
    planks: int
    poomsae: int
    pull_ups: int
    push_ups: int
    raok: int
    rolls_falls: int
    self_defense: int
    sit_ups: int
    sparring: float


class Cycle(Requirements, Metadata, SQLModel, table=True):
    __tablename__ = 'cycles'

    id: int = Field(primary_key=True)
    title: str
    alias: str
    cycle_start: date
    cycle_end: date
    cycle_post_end: Optional[date]
    cycle_pre_start: Optional[date]
    cycle_week_start: int

    candidates: list["Candidate"] = Relationship(back_populates="cycle")


class Candidate(Metadata, SQLModel, table=True):
    __tablename__ = 'candidates'

    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key='users.id')
    cycle_id: int = Field(foreign_key='cycles.id')
    cycle_cont: int
    audit: bool
    hidden: bool
    status: int
    poom: bool
    belt_rank: int
    letters: int
    essays: int
    pre_exam_written: float
    pre_exam_run: float
    pre_exam_push_ups: int
    pre_exam_pull_ups: int
    pre_exam_burpees: int
    pre_exam_planks: int
    exam_written: float
    exam_run: float
    exam_push_ups: int
    exam_pull_ups: int
    exam_burpees: int
    exam_planks: int

    cycle: Cycle = Relationship(back_populates="candidates")
    user: SiteUser = Relationship(back_populates="candidates")

    @property
    def given_name(self) -> str:
        return self.user.given_name


class Tracking(Requirements, Metadata, SQLModel, table=True):
    __tablename__ = 'tracking'
    __table_args__ = (
        Index('idx_tracking_id', 'tracking_date', 'candidate_id', unique=True),
    )

    tracking_date: date = Field(primary_key=True)
    candidate_id: int = Field(primary_key=True)


class JournalPost(Metadata, SQLModel, table=True):
    __tablename__ = 'journal_posts'

    id: int = Field(primary_key=True)
    title: str
    alias: str
    published: bool = Field(default=False)
    content: str = Field(sa_column=Column(TEXT, nullable=True))
