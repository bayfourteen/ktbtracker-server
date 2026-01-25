from crispy_bootstrap5.bootstrap5 import Switch
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from core.models import Tracking


class TrackingForm(forms.ModelForm):
    tracking_date = forms.DateField()
    burpees = forms.IntegerField()
    class_dream_team = forms.BooleanField(initial=False, required=False)
    class_hyper_pro = forms.BooleanField(initial=False, required=False)
    class_master_q = forms.BooleanField(initial=False, required=False)
    class_pmaa = forms.BooleanField(initial=False, required=False)
    class_saturday = forms.BooleanField(initial=False, required=False)
    class_sparring = forms.BooleanField(initial=False, required=False)
    class_weekday = forms.BooleanField(initial=False, required=False)
    journals = forms.IntegerField()
    jumps = forms.IntegerField()
    kicks = forms.IntegerField()
    leadership = forms.IntegerField()
    leadership2 = forms.IntegerField()
    meditation = forms.IntegerField()
    mentee = forms.IntegerField()
    mentor = forms.IntegerField()
    miles = forms.IntegerField()
    planks = forms.IntegerField()
    poomsae = forms.IntegerField()
    pull_ups = forms.IntegerField()
    push_ups = forms.IntegerField()
    raok = forms.IntegerField()
    rolls_falls = forms.IntegerField()
    self_defense = forms.IntegerField()
    sit_ups = forms.IntegerField()
    sparring = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(TrackingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "journals",
            Switch("class_weekday"),
        )

    class Meta:
        model = Tracking
        fields = '__all__'
