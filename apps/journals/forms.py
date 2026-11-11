from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Hidden
from django import forms

from apps.journals.models import JournalPost


class JournalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Hidden("id", self.instance.id),
            "title",
            "content",
        )

    class Meta:
        model = JournalPost
        fields = ('title', 'content')
