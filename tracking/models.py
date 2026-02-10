import dataclasses
from collections import OrderedDict
from dataclasses import dataclass
from datetime import timedelta

from django.utils.translation import gettext_lazy as _

from config.requirements import RequirementsConfig
from core.models import CycleWeek, Candidate, Tracking

TRACKING_NAMES = OrderedDict({e: _(e) for e in (RequirementsConfig.PHYSICAL + RequirementsConfig.CLASS + RequirementsConfig.OTHER)})


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

    def calculate(self):
        eligible_names = [e for e in TRACKING_NAMES.keys() if getattr(self.candidate.cycle, e, 0) > 0]
        start_date = self.cycle_week.start if self.cycle_week else self.candidate.cycle.cycle_start
        end_date = self.cycle_week.end if self.cycle_week else self.candidate.cycle.cycle_end
        candidate_tracking = Tracking.objects.filter(
            candidate=self.candidate,
            tracking_date__gte=start_date,
            tracking_date__lt=end_date + timedelta(days=1)
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

    def calculate(self):
        for cycle_week in range(self.candidate.cycle.cycle_weeks):
            self.weeks.append(TrackingStatistics(candidate=self.candidate, cycle_week=self.candidate.cycle.cycle_week(cycle_week)))

        self.cycle = TrackingStatistics(candidate=self.candidate)

        self.overall = sum(w.overall for w in self.weeks) / len(self.weeks) if self.weeks else 0.0
