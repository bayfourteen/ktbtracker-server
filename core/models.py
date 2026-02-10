from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.db import models

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class CycleWeek:
    week: int
    start: date

    @property
    def days(self) -> list[int]:
        return list(range((self.week * 7), ((self.week * 7) + 7)))

    @property
    def dates(self) -> list[date]:
        return [self.start + timedelta(days=n) for n in range(0, 7)]

    @property
    def end(self) -> date | None:
        return self.start + timedelta(days=6)


class User(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Cycle(models.Model):
    alias = models.CharField(unique=True, max_length=255)
    cycle_end = models.DateField()
    cycle_post_end = models.DateField(blank=True, null=True)
    cycle_pre_start = models.DateField(blank=True, null=True)
    cycle_start = models.DateField()
    cycle_week_start = models.IntegerField()
    burpees = models.IntegerField()
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
    title = models.CharField(max_length=255)
    # -- Metadata --
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'core_cycles'

    @property
    def cycle_days(self) -> int:
        return (self.cycle_end - self.cycle_start).days + 1

    @property
    def cycle_weeks(self) -> int:
        return int(self.cycle_days / 7)

    def cycle_day(self, cycle_date: date = date.today()) -> int:
        return (cycle_date - self.cycle_start).days + 1

    def cycle_week(self, week: int = 0) -> CycleWeek:
        return CycleWeek(week=week, start=self.cycle_start + timedelta(days=week * 7))

    def cycle_week_of(self, cycle_date: date = date.today()) -> CycleWeek:
        return self.cycle_week((cycle_date - self.cycle_start).days // 7)


class Candidate(models.Model):
    audit = models.BooleanField(default=False) # This field type is a guess.
    belt_rank = models.IntegerField(default=0)
    cycle_cont = models.IntegerField(default=0)
    essays = models.IntegerField(default=0)
    exam_written = models.FloatField(default=0)
    hidden = models.BooleanField(default=False) # This field type is a guess.
    letters = models.IntegerField(default=0)
    exam_burpees = models.IntegerField(default=0)
    exam_planks = models.IntegerField(default=0)
    exam_pull_ups = models.IntegerField(default=0)
    exam_push_ups = models.IntegerField(default=0)
    exam_run = models.FloatField(default=0)
    exam_sit_ups = models.IntegerField(default=0)
    pre_exam_burpees = models.IntegerField(default=0)
    pre_exam_planks = models.IntegerField(default=0)
    pre_exam_pull_ups = models.IntegerField(default=0)
    pre_exam_push_ups = models.IntegerField(default=0)
    pre_exam_run = models.FloatField(default=0)
    pre_exam_sit_ups = models.IntegerField(default=0)
    poom = models.BooleanField(default=False)  # This field type is a guess.
    pre_exam_written = models.FloatField(default=0)
    status = models.IntegerField(default=0)
    # -- Metadata --
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.IntegerField(null=True)
    # -- ORM Relationships --
    cycle = models.ForeignKey(Cycle, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'core_candidates'
        unique_together = (('user', 'cycle'),)


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

    class Meta:
        managed = False
        db_table = 'core_tracking'
        unique_together = (('candidate', 'tracking_date'),)


class JournalPost(models.Model):
    title = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    published = models.BooleanField(default=False)  # This field type is a guess.
    content = models.TextField(blank=True, null=True)
    # -- Metadata --
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'core_journal_posts'
