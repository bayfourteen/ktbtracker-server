from datetime import datetime, date, timezone
from typing import Optional, Annotated

import sqlalchemy as sa
from pydantic import computed_field
from sqlmodel import SQLModel, Field, Index, Relationship
from sqlmodel import Column, TEXT

from config.requirements import RequirementsConfig


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

    @computed_field
    @property
    def cycle_days(self) -> int:
        return (self.cycle_end - self.cycle_start).days + 1

    @computed_field
    @property
    def cycle_weeks(self) -> int:
        return int(self.cycle_days / 7)


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


class TrackingFields(SQLModel):
    burpees: float = 0.0
    class_dream_team: float = 0.0
    class_hyper_pro: float = 0.0
    class_master_q: float = 0.0
    class_pmaa: float = 0.0
    class_saturday: float = 0.0
    class_sparring: float = 0.0
    class_weekday: float = 0.0
    journals: float = 0.0
    jumps: float = 0.0
    kicks: float = 0.0
    leadership: float = 0.0
    leadership2: float = 0.0
    meditation: float = 0.0
    mentee: float = 0.0
    mentor: float = 0.0
    miles: float = 0.0
    planks: float = 0.0
    poomsae: float = 0.0
    pull_ups: float = 0.0
    push_ups: float = 0.0
    raok: float = 0.0
    rolls_falls: float = 0.0
    self_defense: float = 0.0
    sit_ups: float = 0.0
    sparring: float = 0.0


class Statistics(SQLModel):
    candidate_id: int
    start_date: date
    end_date: date
    overall: float = 0.0
    totals: TrackingFields = TrackingFields()
    statistics: TrackingFields = TrackingFields()

    def calculate(self, cycle: Cycle) -> None:
        # Calculate the multiplication factor between 0.0 and 1.0 based on the date range of the statistics
        factor = min(max((((self.end_date - self.start_date).days + 1) / cycle.cycle_days), 0.0), 1.0)
        attrs = RequirementsConfig.CLASS + RequirementsConfig.OTHER + RequirementsConfig.PHYSICAL
        attrs = [attr for attr in attrs if getattr(cycle, attr, 0) > 0]

        for attr in attrs:
            if factor > 0.0:
                setattr(self.statistics, attr, getattr(self.totals, attr, 0) / (getattr(cycle, attr) * factor))
            else:
                setattr(self.statistics, attr, 0)

        self.overall = sum([getattr(self.statistics, attr, 0) for attr in attrs]) / len(attrs) if len(attrs) > 0 else 0.0


class FullStatistics(SQLModel):
    candidate_id: int
    start_date: date
    end_date: date
    overall: float = 0.0
    weeks: list[Statistics] = list()
