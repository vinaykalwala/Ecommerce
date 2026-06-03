from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random
import string

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('superuser', 'Superuser'),
    )
    
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    mobile_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "mobile_number"]

    def __str__(self):
        return f"{self.email} ({self.user_type})"
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.user_type = 'superuser'
        elif self.user_type == 'superuser':
            self.is_superuser = True
            self.is_staff = True
        elif self.user_type == 'admin':
            self.is_staff = True
        super().save(*args, **kwargs)


class OTPVerification(models.Model):
    OTP_TYPES = (
        ('signup', 'Signup'),
        ('forgot_password', 'Forgot Password'),
        ('change_password', 'Change Password'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES)
    destination = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()
    
    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    
    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )
    
    gender = models.CharField(
        max_length=20, 
        choices=(
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say')
        ),
        blank=True
    )
    
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    facebook_profile = models.URLField(blank=True, null=True)
    instagram_profile = models.URLField(blank=True, null=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.email}"


class Address(models.Model):
    ADDRESS_TYPES = (
        ("home", "Home"),
        ("office", "Office"),
        ("other", "Other"),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    
    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPES
    )
    
    full_name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=15)
    alternate_mobile_number = models.CharField(max_length=15, blank=True)
    
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    landmark = models.CharField(max_length=255, blank=True)
    delivery_instructions = models.TextField(max_length=500, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_billing_address = models.BooleanField(default=False)
    is_shipping_address = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.address_type} - {self.full_name}, {self.city}"


class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    attempt_time = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-attempt_time']