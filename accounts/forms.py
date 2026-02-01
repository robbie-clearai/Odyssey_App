from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    lga = forms.ChoiceField(
        choices=User.LGA.choices,
        label='Local Government Area',
        help_text='Select the LGA where you reside'
    )
    child_safety_acknowledged = forms.BooleanField(
        required=True,
        label='I acknowledge the child safety guidelines'
    )
    data_privacy_agreed = forms.BooleanField(
        required=True,
        label='I agree to the data privacy policy'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'lga', 'password1', 'password2',
                  'child_safety_acknowledged', 'data_privacy_agreed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['child_safety_acknowledged', 'data_privacy_agreed']:
                field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'lga', 'email_notifications_enabled']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent'
