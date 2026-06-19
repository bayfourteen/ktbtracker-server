from django.db import models

from .cycles import Cycle
from .users import User


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
        db_table = 'ktbtracker_candidates'
        unique_together = (('user', 'cycle'),)

