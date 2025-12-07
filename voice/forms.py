from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, label="Role")
    county = forms.ChoiceField(choices=Profile.COUNTY_CHOICES, label="County")
    constituency = forms.ChoiceField(choices=Profile.CONSTITUENCY_CHOICES, label="Constituency")
    ward = forms.ChoiceField(choices=Profile.WARD_CHOICES, label="Ward")



    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role", "county", "constituency", "ward" ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': field_name.capitalize()
            })

        self.fields['username'].widget.attrs.update({'autofocus': True})
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
