from django.db import models
from accounts.models import User
from catalog.models import ProductVariant
from core.models import BaseModel


class Order(BaseModel):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("payment_pending", "Payment Pending"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("returned", "Returned"),
        ("refunded", "Refunded"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders"
    )

    order_number = models.CharField(
        max_length=50,
        unique=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    notes = models.TextField(
        blank=True
    )


class OrderAddress(BaseModel):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=200)

    mobile_number = models.CharField(max_length=15)

    address_line_1 = models.CharField(max_length=255)

    address_line_2 = models.CharField(
        max_length=255,
        blank=True
    )

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    country = models.CharField(max_length=100)

    postal_code = models.CharField(max_length=20)


class OrderItem(BaseModel):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True
    )

    product_name = models.CharField(
        max_length=255
    )

    sku = models.CharField(
        max_length=100
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )