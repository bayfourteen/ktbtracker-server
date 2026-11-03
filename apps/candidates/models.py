from django.db import models
from django.db.models import Model

from apps.cycles.models import Cycle
from apps.users.models import User
from config import settings
from apps.ktbtracker.models import BeltRank, Status
from apps.journals.models import JournalPost


class Candidate(models.Model):
    audit = models.BooleanField(default=False)  # This field type is a guess.
    belt_rank = models.IntegerField(default=0, choices=BeltRank.choices)
    cycle_cont = models.IntegerField(default=0)
    essays = models.IntegerField(default=0)
    exam_written = models.FloatField(default=0)
    hidden = models.BooleanField(default=False)  # This field type is a guess.
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
    status = models.IntegerField(default=0, choices=Status.choices)
    # -- Metadata --
    created = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(default=0)
    modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.IntegerField(null=True)
    # -- ORM Relationships --
    cycle = models.ForeignKey(Cycle, models.DO_NOTHING, related_name="candidates")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, related_name="candidates")

    @property
    def get_audit_display(self) -> str:
        return '<i class="text-success bi bi-check-circle-fill"></i>' if self.audit else '-'

    @property
    def get_candidate_name(self) -> str:
        return f"{self.user.first_name.capitalize() + ' ' if self.user.first_name else ''}"\
               f"{self.user.last_name.capitalize() + ' ' if self.user.last_name else ''}"\
               f"({self.user.username})"

    @property
    def get_hidden_display(self) -> str:
        return '<i class="text-{} bi bi-{}"></i>'.format(
            "danger" if self.hidden else "success",
            "x-circle-fill" if self.hidden else "check-circle-fill")
        #return "-" if self.hidden else '<i class="text-success bi bi-check-circle-fill"></i>'

    @property
    def get_last_journaled_display(self) -> str:
        return JournalPost.objects.filter(created_by=self.user_id).order_by("-created").first().created.strftime("%Y-%m-%d") \
            if JournalPost.objects.filter(created_by=self.user_id).exists() else "-"

    @property
    def get_last_tracked_display(self) -> str:
        return self.tracking.filter(candidate=self).first().created.strftime("%Y-%m-%d") \
            if self.tracking.filter(candidate=self).exists() else "-"

    @property
    def get_poom_display(self) -> str:
        return '<i class="text-success bi bi-check-circle-fill"></i>' if self.poom else '-'

    class Meta:
        unique_together = (("user", "cycle"),)

