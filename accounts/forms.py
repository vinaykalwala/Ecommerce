from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from .models import User, UserProfile, Address, OTPVerification
import re
from django.conf import settings

class PhoneNumberValidator:
    def __call__(self, value):
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise forms.ValidationError('Enter a valid phone number.')

class BaseSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    mobile_number = forms.CharField(
        max_length=15, 
        required=True,
        validators=[PhoneNumberValidator()],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'})
    )
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    
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
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.')
        return email
    
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if User.objects.filter(mobile_number=mobile).exists():
            raise forms.ValidationError('Mobile number already registered.')
        return mobile

class CustomerSignupForm(BaseSignupForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        if commit:
            user.save()
        return user

class AdminSignupForm(BaseSignupForm):
    admin_code = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Admin Registration Code'})
    )
    
    def clean_admin_code(self):
        admin_code = self.cleaned_data.get('admin_code')
        # Get admin code from settings, with a default fallback
        expected_code = getattr(settings, 'ADMIN_REGISTRATION_CODE', 'ADMIN2024')
        if admin_code != expected_code:
            raise forms.ValidationError('Invalid admin registration code')
        return admin_code
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'admin'
        if commit:
            user.save()
            from django.contrib.auth.models import Permission
            permissions = Permission.objects.filter(
                codename__in=['view_user', 'change_user', 'view_product', 'change_product', 'view_order', 'change_order']
            )
            user.user_permissions.set(permissions)
        return user

class SuperuserSignupForm(BaseSignupForm):
    superuser_code = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Superuser Registration Code'})
    )
    
    def clean_superuser_code(self):
        superuser_code = self.cleaned_data.get('superuser_code')
        # Get superuser code from settings, with a default fallback
        expected_code = getattr(settings, 'SUPERUSER_REGISTRATION_CODE', 'SUPER2024')
        if superuser_code != expected_code:
            raise forms.ValidationError('Invalid superuser registration code')
        return superuser_code
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'superuser'
        user.is_superuser = True
        user.is_staff = True
        if commit:
            user.save()
        return user

class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit OTP'})
    )

class LoginForm(forms.Form):
    login_input = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email / Username / Mobile Number'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    captcha = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter captcha'})
    )

class ForgotPasswordForm(forms.Form):
    contact_info = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email or Mobile Number'
        })
    )

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "profile_picture",
            "gender",
            "date_of_birth",
            "bio",
            "facebook_profile",
            "instagram_profile",
            "twitter_handle",
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'facebook_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Facebook Profile URL'}),
            'instagram_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Instagram Profile URL'}),
            'twitter_handle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile_number",
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ["user"]
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'alternate_mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternate Mobile Number'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Landmark'}),
            'delivery_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Delivery Instructions'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_billing_address': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_shipping_address': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }