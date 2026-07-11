from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class KTBAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-12'),
                Column('password', css_class='col-12'),
                Column('remember_me', css_class='col-12'),
                Column(
                    Submit('submit', _('Log in now'), css_class='btn-primary btn-lg'),
                    css_class='col-md-12'
                ),
                css_class="row gy-3 overflow-hidden",
            ),
        )
