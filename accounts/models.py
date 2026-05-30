from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel


class User(AbstractUser):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class UserProfile(BaseModel):
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

    gender = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)


class Address(BaseModel):

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

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    postal_code = models.CharField(max_length=20)

    landmark = models.CharField(
        max_length=255,
        blank=True
    )

    is_default = models.BooleanField(default=False)