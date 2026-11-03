from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms.models import ModelChoiceField


class User(AbstractUser):
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class UserChoiceField(ModelChoiceField):
    def label_from_instance(self, obj: User):
        return f"{obj.last_name + ', ' if obj.last_name else ''}{obj.first_name} ({obj.username})"
