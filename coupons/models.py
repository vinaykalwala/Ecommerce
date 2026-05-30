# coupons/models.py

from django.db import models

from core.models import BaseModel


class Coupon(BaseModel):

    DISCOUNT_TYPES = (
        ("fixed", "Fixed"),
        ("percentage", "Percentage"),
    )

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPES
    )

    value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    usage_limit = models.PositiveIntegerField(
        default=1000
    )

    used_count = models.PositiveIntegerField(
        default=0
    )

    valid_from = models.DateTimeField()

    valid_to = models.DateTimeField()

    is_active = models.BooleanField(
        default=True
    )

    @property
    def discount_amount(self):

        if not self.coupon:
            return 0

        from coupons.services import (
            validate_coupon,
            calculate_discount
        )

        valid, message = validate_coupon(
            self.coupon,
            self.subtotal
        )

        if not valid:
            return 0

        return calculate_discount(
            self.coupon,
            self.subtotal
        )

    def __str__(self):
        return self.code

class CouponUsage(BaseModel):

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )