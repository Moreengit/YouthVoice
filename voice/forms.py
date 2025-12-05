# from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm

# class RegisterForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)

#     class Meta:
#         model = User
#         fields = ["username", "first_name", "last_name", "email", "password1", "password2"]




from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].widget.attrs.update({'autofocus': True})
        

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': field_name.capitalize()
            })