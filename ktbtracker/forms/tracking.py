import logging
from collections import OrderedDict

from crispy_bootstrap5.bootstrap5 import Switch
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden
from django import forms
from django.db import models
from django.forms import fields
from django.utils.translation import gettext_lazy as _

from config.requirements import Requirements
from ktbtracker import debug
from ktbtracker.models import Tracking, Cycle, Candidate


#TRACKING_NAMES = OrderedDict({e.key: e.title for e in Requirements})

INTEGER_INPUT_WIDGET = forms.NumberInput(attrs={"min": "0", "step": "1", "pattern": r"^\d+$"})
FLOAT_INPUT_WIDGET = forms.NumberInput(attrs={"min": "0", "pattern": r"^\d+(?:\.\d+)?$"})

logger = logging.getLogger(__name__)


class TrackingForm(forms.ModelForm):
    tracking_date = forms.DateField(widget=forms.DateInput(attrs={"class": "datepicker"}))

    def __init__(self, *args, **kwargs):
        self.candidate = kwargs.pop("candidate", Candidate())
        super(TrackingForm, self).__init__(*args, **kwargs)

        logger.info(f"{kwargs=} {self.fields=}")

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.fields["tracking_date"] = forms.DateField(widget=forms.DateInput(attrs={"class": "datepicker"}))

        for e in [e for e in Requirements if getattr(self.candidate.cycle, e.key, 0) > 0]:
            logger.debug(f"Adding {e.key} {type(self.fields[e.key])} {isinstance(self.fields[e.key], fields.FloatField)}")
            if isinstance(self.fields[e.key], fields.FloatField):
                self.fields[e.key] = forms.FloatField(
                    label=e.title,
                    widget=forms.NumberInput(
                        attrs=dict(**self.fields[e.key].widget.attrs)),
                    min_value=0,
                    required=False
                )
            else:
                self.fields[e.key] = forms.IntegerField(
                    label=e.title,
                    widget=forms.NumberInput(
                        attrs=dict(**self.fields[e.key].widget.attrs, pattern=r"^\d+$")),
                    min_value=0,
                    step_size=1,
                    initial=getattr(self.candidate.cycle, e.key, 0),
                    required=False
                )

        # Override any valid CLASS fields as BooleanField
        for e in [e for e in Requirements.CLASS() if getattr(self.candidate.cycle, e.key, 0) > 0]:
            logger.info(f"{type(self.instance)} {getattr(self.instance, e.key, None)}")
            self.fields[e.key] = forms.BooleanField(
                label=e.title,
                widget=forms.CheckboxInput(
                    attrs=dict(**self.fields[e.key].widget.attrs),
                    check_test=lambda value: value == 1),
                initial=getattr(self.instance, e.key, 0) == 1,
                disabled=(
                        (self.instance.tracking_date.weekday() > 5) or
                        (self.instance.tracking_date.weekday() == 5 and e.key != "class_saturday") or
                        (self.instance.tracking_date.weekday() < 5 and e.key == "class_saturday")
                ),
                required=False)

        # Remove any invalid fields
        for name in [e.key for e in Requirements if getattr(self.candidate.cycle, e.key, 0) == 0]:
            del self.fields[name]

        self.helper.layout = Layout(
            Hidden("id", self.instance.id),
            Hidden("tracking_date", self.instance.tracking_date),
            Hidden("candidate", self.instance.candidate.id),
            *[e.key for e in Requirements.PHYSICAL() if getattr(self.candidate.cycle, e.key, 0) > 0],
            *[Switch(e.key, wrapper_class="form-check-reverse") for e in Requirements.CLASS() if getattr(self.candidate.cycle, e.key, 0) > 0],
            *[e.key for e in Requirements.OTHER() if getattr(self.candidate.cycle, e.key, 0) > 0]
        )

    class Meta:
        model = Tracking
        fields = list(Requirements.TRACKING_NAMES().keys())
