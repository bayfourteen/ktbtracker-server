from django.db import models

from config import settings


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
    # -- ORM Relationships --
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING)