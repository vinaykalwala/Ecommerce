from django.db import models

from accounts.models import User
from catalog.models import Product

from core.models import BaseModel


class ProductView(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="views"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

class SearchLog(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    query = models.CharField(
        max_length=255
    )

class UserActivity(BaseModel):

    ACTIVITY_TYPES = (

        ("login", "Login"),

        ("signup", "Signup"),

        ("add_to_cart", "Add To Cart"),

        ("wishlist", "Wishlist"),

        ("order", "Order"),

        ("review", "Review"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPES
    )

    description = models.CharField(
        max_length=255
    )

