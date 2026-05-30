from django.db import models

from orders.models import Order
from core.models import BaseModel


class Payment(BaseModel):

    STATUS_CHOICES = (
        ("created", "Created"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    gateway = models.CharField(
        max_length=50,
        default="razorpay"
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        blank=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True
    )

    transaction_id = models.CharField(
        max_length=255,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    response_data = models.JSONField(
        null=True,
        blank=True
    )