# core/forms.py
# Registration form — like a controlled form with validation

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    risk_profile = forms.ChoiceField(
        choices=[
            ("conservative", "Conservative (careful)"),
            ("moderate", "Moderate (balanced)"),
            ("aggressive", "Aggressive (bold)"),
        ],
        initial="moderate",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
