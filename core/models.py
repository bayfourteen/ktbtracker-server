
from pathlib import Path

from django.db import models

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


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
    cycle = models.ForeignKey('Cycles', models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'candidates'
        unique_together = (('user', 'cycle'),)


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


class Tracking(models.Model):
    pk = models.CompositePrimaryKey('candidate_id', 'tracking_date')
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


class UserUsergroups(models.Model):
    pk = models.CompositePrimaryKey('usergroup_id', 'user_id')
    usergroup = models.ForeignKey('Usergroups', models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_usergroups'


class Usergroups(models.Model):
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'usergroups'


class Users(models.Model):
    display_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255)
    email_verified = models.TextField()  # This field type is a guess.
    photo_url = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'users'
