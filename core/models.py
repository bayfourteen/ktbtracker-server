from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

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


class Users(models.Model):
    display_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255)
    email_verified = models.TextField()  # This field type is a guess.
    photo_url = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'users'


class Usergroups(models.Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'usergroups'


class UserUsergroups(models.Model):
    pk = models.CompositePrimaryKey('usergroup_id', 'user_id')
    usergroup = models.ForeignKey(Usergroups, models.DO_NOTHING)
    user = models.ForeignKey(Users, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_usergroups'


class Cycles(models.Model):
    alias = models.CharField(unique=True, max_length=255)
    cycle_end = models.DateField()
    cycle_post_end = models.DateField(blank=True, null=True)
    cycle_pre_start = models.DateField(blank=True, null=True)
    cycle_start = models.DateField()
    cycle_week_start = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=255, blank=True, null=True)
    burpees = models.IntegerField()
    class_dream_team = models.IntegerField()
    class_hyper_pro = models.IntegerField()
    class_master_q = models.IntegerField()
    class_pmaa = models.IntegerField()
    class_saturday = models.IntegerField()
    class_sparring = models.IntegerField()
    class_weekday = models.IntegerField()
    journals = models.IntegerField()
    jumps = models.FloatField()
    kicks = models.IntegerField()
    leadership = models.IntegerField()
    leadership2 = models.IntegerField()
    meditation = models.FloatField()
    mentee = models.IntegerField()
    mentor = models.IntegerField()
    miles = models.FloatField()
    planks = models.IntegerField()
    poomsae = models.IntegerField()
    pull_ups = models.IntegerField()
    push_ups = models.IntegerField()
    raok = models.IntegerField()
    rolls_falls = models.IntegerField()
    self_defense = models.IntegerField()
    sit_ups = models.IntegerField()
    sparring = models.FloatField()
    title = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'cycles'

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


class Candidates(models.Model):
    audit = models.TextField()  # This field type is a guess.
    belt_rank = models.IntegerField()
    cycle_cont = models.IntegerField()
    essays = models.IntegerField()
    exam_written = models.FloatField()
    hidden = models.TextField()  # This field type is a guess.
    letters = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=255, blank=True, null=True)
    exam_burpees = models.IntegerField()
    exam_planks = models.IntegerField()
    exam_pull_ups = models.IntegerField()
    exam_push_ups = models.IntegerField()
    exam_run = models.FloatField()
    exam_sit_ups = models.IntegerField()
    pre_exam_burpees = models.IntegerField()
    pre_exam_planks = models.IntegerField()
    pre_exam_pull_ups = models.IntegerField()
    pre_exam_push_ups = models.IntegerField()
    pre_exam_run = models.FloatField()
    pre_exam_sit_ups = models.IntegerField()
    poom = models.TextField()  # This field type is a guess.
    pre_exam_written = models.FloatField()
    status = models.IntegerField()
    cycle = models.ForeignKey(Cycles, models.DO_NOTHING)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'candidates'
        unique_together = (('user', 'cycle'),)


class Tracking(models.Model):
    tracking_date = models.DateField()
    burpees = models.IntegerField()
    class_dream_team = models.IntegerField()
    class_hyper_pro = models.IntegerField()
    class_master_q = models.IntegerField()
    class_pmaa = models.IntegerField()
    class_saturday = models.IntegerField()
    class_sparring = models.IntegerField()
    class_weekday = models.IntegerField()
    journals = models.IntegerField()
    jumps = models.FloatField()
    kicks = models.IntegerField()
    leadership = models.IntegerField()
    leadership2 = models.IntegerField()
    meditation = models.FloatField()
    mentee = models.IntegerField()
    mentor = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=255, blank=True, null=True)
    miles = models.FloatField()
    planks = models.IntegerField()
    poomsae = models.IntegerField()
    pull_ups = models.IntegerField()
    push_ups = models.IntegerField()
    raok = models.IntegerField()
    rolls_falls = models.IntegerField()
    self_defense = models.IntegerField()
    sit_ups = models.IntegerField()
    sparring = models.FloatField()
    candidate = models.ForeignKey(Candidates, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tracking'
        unique_together = (('candidate', 'tracking_date'),)


class JournalPosts(models.Model):
    alias = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=255, blank=True, null=True)
    published = models.TextField()  # This field type is a guess.
    title = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'journal_posts'
