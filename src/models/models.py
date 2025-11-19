from dataclasses import dataclass
from datetime import datetime, date, timedelta, timezone
from enum import Enum
from typing import ClassVar, Any, Sequence

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic.alias_generators import to_camel


PREFIXES = ["mr", "mrs", "ms", "miss", "dr", "hon", "mayor", "president", "pres", "master", "grandmaster"]
SUFFIXES = ["jr", "sr", "iii", "iv", "phd", "md", "dds", "od", "ret"]


class FormatStyle(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    ABBREVIATED = "abbrev"
    SORTED = "sorted"


@dataclass
class PersonNameComponents:
    _person_name: str

    name_prefix: str | None
    given_name: str | None
    middle_name: str | None
    family_name: str | None
    name_suffix: str | None
    nickname: str | None
    phonetic_representation: str | None

    def __init__(self, person_name: str, **kwargs: Any):
        super().__init__(**kwargs)
        self._person_name = person_name or ""

        components = person_name.replace(",", "").split()

        #
        # If there are 3 or more components, the name _may_ have a prefix and/or suffix...
        #
        if len(components) > 2:
            # If the first component matches a known prefix, extract it and remove it
            if len(components) > 1 and components[0].replace(".", "").lower() in PREFIXES:
                self.name_prefix = components[0]
                components = components[1:]
            else:
                self.name_prefix = None

            # IF the last component matches a known suffix, extract it and remove it
            if len(components) > 1 and components[-1].replace(".", "").lower() in SUFFIXES:
                self.name_suffix = components[-1]
                components = components[:-1]
            else:
                self.name_suffix = None
        else:
            self.name_prefix = None
            self.name_suffix = None

        if len(components) > 2:
            self.given_name = components[0]
            self.family_name = components[-1]
            self.middle_name = " ".join(components[1:-1])
        elif len(components) > 1:
            self.given_name = components[0]
            self.family_name = components[-1]
            self.middle_name = None
        else:
            self.given_name = components[0]
            self.family_name = None
            self.middle_name = None

    @property
    def full_name(self) -> str:
        return self.formatted(FormatStyle.LONG)

    @property
    def initials(self) -> str:
        return self.formatted(FormatStyle.ABBREVIATED)

    def formatted(self, style: FormatStyle = FormatStyle.LONG) -> str:
        match style:
            case FormatStyle.SHORT:
                return f"{self.given_name.title()}".strip() if self.given_name else ""
            case FormatStyle.MEDIUM:
                return "".join(
                    [
                        f"{self.given_name.title()}" if self.given_name else "",
                        f" {self.family_name.title()[0]}." if self.family_name else "",
                     ]
                ).strip()
            case FormatStyle.LONG:
                return "".join(
                    [
                        f"{self.name_prefix.title()}" if self.name_prefix else "",
                        f" {self.given_name.title()}" if self.given_name else "",
                        f" {self.middle_name.title()}" if self.middle_name else "",
                        f" {self.family_name.title()}" if self.family_name else "",
                        f" {self.name_suffix.title()}" if self.name_suffix else "",
                    ]
                ).strip()
            case FormatStyle.ABBREVIATED:
                return "".join(
                    [
                        (self.given_name or "")[0],
                        (self.middle_name or "")[0],
                        (self.family_name or "")[0],
                    ]
                ).strip()
            case FormatStyle.SORTED:
                sorted_name = "".join(
                    [
                        f"{self.family_name}" if self.family_name else "",
                        f" {self.name_suffix}," if self.name_suffix else ",",
                        f" {self.name_prefix}" if self.name_prefix else "",
                        f" {self.given_name}" if self.given_name else "",
                        f" {self.middle_name}" if self.middle_name else "",
                    ]
                ).strip()
                return "" if sorted_name == "," else sorted_name[2:] if sorted_name.startswith(",") else sorted_name

    def __str__(self) -> str:
        return "PersonNameComponents("\
               f"_person_name={self._person_name}"\
               f", name_prefix={self.name_prefix}"\
               f", given_name={self.given_name}"\
               f", middle_name={self.middle_name}"\
               f", family_name={self.family_name}"\
               f", name_suffix={self.name_suffix}"\
               ")"

    def __repr__(self) -> str:
        return f"PersonNameComponents('{self._person_name}')"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        json_encoders={datetime: lambda dt: dt.strftime('%Y-%m-%dT%H:%M:%SZ')},
        from_attributes=True,
        populate_by_name=True)


class SiteGroup(ConfiguredBaseModel):
    id: int
    name: str
    description: str | None


class SiteUser(ConfiguredBaseModel):
    id: int
    user_id: str
    display_name: str
    email: str
    email_verified: bool
    photo_url: str | None

    _person_name: PersonNameComponents

    def model_post_init(self, context: Any, /) -> None:
        self._person_name = PersonNameComponents(self.display_name)

    @computed_field
    @property
    def given_name(self) -> str:
        return self._person_name.given_name

    @computed_field
    @property
    def family_name(self) -> str:
        return self._person_name.family_name

    @computed_field
    @property
    def sorted_name(self) -> str:
        return self._person_name.formatted(FormatStyle.SORTED)


class Metadata(ConfiguredBaseModel):
    created_by: int = 0
    created: datetime = datetime.now(timezone.utc)
    modified_by: int | None = None
    modified: datetime | None = None


class Requirements(ConfiguredBaseModel):
    burpees: int = 0
    class_dream_team: int = 0
    class_hyper_pro: int = 0
    class_master_q: int = 0
    class_pmaa: int = 0
    class_saturday: int = 0
    class_sparring: int = 0
    class_weekday: int = 0
    journals: int = 0
    jumps: float = 0.0
    kicks: int = 0
    leadership: int = 0
    leadership2: int = 0
    meditation: float = 0.0
    mentee: int = 0
    mentor: int = 0
    miles: float = 0.0
    planks: int = 0
    poomsae: int = 0
    pull_ups: int = 0
    push_ups: int = 0
    raok: int = 0
    rolls_falls: int = 0
    self_defense: int = 0
    sit_ups: int = 0
    sparring: float = 0.0


class CycleWeek(BaseModel):
    days: list[date]

    @computed_field
    @property
    def start(self) -> date | None:
        return self.days[0] or None

    @computed_field
    @property
    def end(self) -> date | None:
        return self.days[-1] or None


class Cycle(Requirements, Metadata, ConfiguredBaseModel):
    id: int = 0
    title: str = ""
    alias: str = ""
    cycle_start: date = date.today()
    cycle_end: date = date.today()
    cycle_pre_start: date | None = None
    cycle_post_end: date | None = None
    cycle_week_start: int = 6

    @computed_field
    @property
    def cycle_days(self) -> int:
        return (self.cycle_end - self.cycle_start).days + 1

    @computed_field
    @property
    def cycle_weeks(self) -> int:
        return int(self.cycle_days / 7)

    def cycle_day(self, date: date = date.today()) -> int:
        return (date - self.cycle_start).days + 1

    def cycle_week(self, week: int = 0) -> CycleWeek:
        start_date = self.cycle_start + timedelta(days=week * 7)

        return CycleWeek(days=[start_date + timedelta(days=n) for n in range(0, 7)])


class Candidate(Metadata, ConfiguredBaseModel):
    id: int
    user_id: int
    cycle_id: int
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

    user: SiteUser

    @computed_field
    @property
    def given_name(self) -> str:
        return self.user.given_name


class Tracking(Requirements, Metadata, ConfiguredBaseModel):
    tracking_date: date
    candidate_id: int


class JournalPost(Metadata, ConfiguredBaseModel):
    id: int
    title: str
    alias: str
    published: bool
    content: str


class TrackingFields(ConfiguredBaseModel):
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


class TrackingTotals(ConfiguredBaseModel):
    candidate_id: int
    start_date: date
    end_date: date
    totals: TrackingFields = TrackingFields()


class Statistics(ConfiguredBaseModel):
    candidate_id: int
    start_date: date
    end_date: date
    overall: float = 0.0
    totals: TrackingFields = TrackingFields()
    statistics: TrackingFields = TrackingFields()


class FullStatistics(Statistics, ConfiguredBaseModel):
    weeks: list[Statistics] = list()
