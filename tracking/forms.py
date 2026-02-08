import logging
from collections import OrderedDict

from crispy_bootstrap5.bootstrap5 import Switch
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.db import models
from django.forms import fields
from django.utils.translation import gettext_lazy as _

from config.requirements import RequirementsConfig
from core.models import Tracking, Cycles

TRACKING_NAMES = OrderedDict(
    {e: _(e) for e in (RequirementsConfig.PHYSICAL + RequirementsConfig.CLASS + RequirementsConfig.OTHER)})

INTEGER_INPUT_WIDGET = forms.NumberInput(attrs={"min": "0", "step": "1", "pattern": r"^\d+$"})
FLOAT_INPUT_WIDGET = forms.NumberInput(attrs={"min": "0", "pattern": r"^\d+(?:\.\d+)?$"})

logger = logging.getLogger(__name__)


class TrackingForm(forms.ModelForm):
    tracking_date = forms.DateField(widget=forms.DateInput(attrs={"class": "datepicker"}))

    def __init__(self, *args, **kwargs):
        self.cycle = kwargs.pop("cycle", Cycles())
        super(TrackingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.fields["tracking_date"] = forms.DateField(widget=forms.DateInput(attrs={"class": "datepicker"}))

        for name in [name for name in RequirementsConfig.PHYSICAL + RequirementsConfig.OTHER if getattr(self.cycle, name, 0) > 0]:
            logger.debug(f"Adding {name} {type(self.fields[name])} {isinstance(self.fields[name], fields.FloatField)}")
            if isinstance(self.fields[name], fields.FloatField):
                self.fields[name] = forms.FloatField(
                    label=_(name),
                    widget=forms.NumberInput(
                        attrs=dict(**self.fields[name].widget.attrs)),
                    min_value=0,
                    required=False
                )
            else:
                self.fields[name] = forms.IntegerField(
                    label=_(name),
                    widget=forms.NumberInput(
                        attrs=dict(**self.fields[name].widget.attrs, pattern=r"^\d+$")),
                    min_value=0,
                    step_size=1,
                    initial=getattr(self.cycle, name, 0),
                    required=False
                )

        # Override any valid CLASS fields as BooleanField
        for name in [name for name in RequirementsConfig.CLASS if getattr(self.cycle, name, 0) > 0]:
            logger.info(f"{type(self.instance)} {getattr(self.instance, name, None)}")
            self.fields[name] = forms.BooleanField(
                label=_(name),
                widget=forms.CheckboxInput(
                    attrs=dict(**self.fields[name].widget.attrs),
                    check_test=lambda value: value == 1),
                initial=getattr(self.instance, name, 0) == 1,
                required=False)

        # Remove any invalid fields
        for name in [name for name in TRACKING_NAMES if getattr(self.cycle, name, 0) == 0]:
            del self.fields[name]

        self.helper.layout = Layout(
            *[name for name in RequirementsConfig.PHYSICAL if getattr(self.cycle, name, 0) > 0],
            *[Switch(name, wrapper_class="form-check-reverse") for name in RequirementsConfig.CLASS if getattr(self.cycle, name, 0) > 0],
            *[name for name in RequirementsConfig.OTHER if getattr(self.cycle, name, 0) > 0]
        )

    class Meta:
        model = Tracking
        fields = '__all__'
