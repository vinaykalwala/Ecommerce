from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile, Address


class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "mobile_number",
            "password1",
            "password2",
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "profile_picture",
            "gender",
            "date_of_birth",
        ]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile_number",
        ]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ["user"]