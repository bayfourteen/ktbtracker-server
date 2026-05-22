import dataclasses
from collections import OrderedDict
from dataclasses import dataclass
from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _

from config.requirements import Requirements
from .candidates import Candidate
from .cycles import CycleWeek
from .. import debug

TRACKING_NAMES = OrderedDict({e.key: e.title for e in Requirements})


class Tracking(models.Model):
    tracking_date = models.DateField()
    burpees = models.IntegerField(default=0)
    class_dream_team = models.IntegerField(default=0)
    class_hyper_pro = models.IntegerField(default=0)
    class_master_q = models.IntegerField(default=0)
    class_pmaa = models.IntegerField(default=0)
    class_saturday = models.IntegerField(default=0)
    class_sparring = models.IntegerField(default=0)
    class_weekday = models.IntegerField(default=0)
    journals = models.IntegerField(default=0)
    jumps = models.FloatField(default=0)
    kicks = models.IntegerField(default=0)
    leadership = models.IntegerField(default=0)
    leadership2 = models.IntegerField(default=0)
    meditation = models.FloatField(default=0)
    mentee = models.IntegerField(default=0)
    mentor = models.IntegerField(default=0)
    miles = models.FloatField(default=0)
    planks = models.IntegerField(default=0)
    poomsae = models.IntegerField(default=0)
    pull_ups = models.IntegerField(default=0)
    push_ups = models.IntegerField(default=0)
    raok = models.IntegerField(default=0)
    rolls_falls = models.IntegerField(default=0)
    self_defense = models.IntegerField(default=0)
    sit_ups = models.IntegerField(default=0)
    sparring = models.FloatField(default=0)
    # -- Metadata --
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.IntegerField(null=True)
    # -- ORM Relationships --
    candidate = models.ForeignKey(Candidate, models.DO_NOTHING)


# Create your models here.
@dataclass
class TrackingFields:
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


@dataclass
class TrackingStatistics:
    candidate: Candidate
    cycle_week: CycleWeek | None = None
    overall: float = 0.0
    totals: TrackingFields = dataclasses.field(default_factory=TrackingFields)
    statistics: TrackingFields = dataclasses.field(default_factory=TrackingFields)

    def __post_init__(self):
        self.calculate()

    @debug
    def calculate(self):
        eligible_names = [e for e in TRACKING_NAMES.keys() if getattr(self.candidate.cycle, e, 0) > 0]
        start_date = self.cycle_week.start if self.cycle_week else self.candidate.cycle.cycle_start
        end_date = self.cycle_week.end if self.cycle_week else self.candidate.cycle.cycle_end
        candidate_tracking = Tracking.objects.select_related("candidate").filter(
            candidate=self.candidate,
            tracking_date__range=(start_date, end_date + timedelta(days=1))
        )

        # Calculate the multiplication factor between 0.0 and 1.0 based on the date range of the statistics
        factor = min(max((((end_date - start_date).days + 1) / self.candidate.cycle.cycle_days), 0.0), 1.0)

        for name in eligible_names:
            setattr(self.totals, name, sum([getattr(t, name, 0) for t in list(candidate_tracking)]))
            if factor > 0.0:
                setattr(self.statistics, name, getattr(self.totals, name, 0) / (getattr(self.candidate.cycle, name) * factor))
            else:
                setattr(self.statistics, name, 0)

        self.overall = sum([getattr(self.statistics, name, 0) for name in eligible_names]) / len(eligible_names) if len(eligible_names) > 0 else 0.0


@dataclass
class TrackingFullStatistics:
    candidate: Candidate
    overall: float = 0.0
    cycle: TrackingStatistics = None
    weeks: list[TrackingStatistics] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.calculate()

    @debug
    def calculate(self):
        for cycle_week in range(self.candidate.cycle.cycle_weeks):
            self.weeks.append(TrackingStatistics(candidate=self.candidate, cycle_week=self.candidate.cycle.cycle_week(cycle_week)))

        self.cycle = TrackingStatistics(candidate=self.candidate)

        self.overall = sum(w.overall for w in self.weeks) / len(self.weeks) if self.weeks else 0.0
