from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Column, Row
from django import forms


class AccountsLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-12'),
                Column('password', css_class='col-12'),
                Column('remember_me', css_class='col-12'),
                css_class="row gy-3 overflow-hidden",
            ),
        )
