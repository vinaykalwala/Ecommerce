from django.db import models

from accounts.models import User
from catalog.models import ProductVariant
from coupons.models import Coupon

from core.models import BaseModel


class Cart(BaseModel):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart"
    )

    session_key = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.user:
            return f"{self.user.email} Cart"
        return f"Session Cart {self.id}"

    @property
    def subtotal(self):
        return sum(
            item.line_total
            for item in self.items.all()
        )

    @property
    def discount_amount(self):

        if not self.coupon:
            return 0

        if self.coupon.discount_type == "fixed":
            return min(
                self.coupon.value,
                self.subtotal
            )

        if self.coupon.discount_type == "percentage":
            return (
                self.subtotal
                * self.coupon.value
                / 100
            )

        return 0

    @property
    def total(self):
        return self.subtotal - self.discount_amount


class CartItem(BaseModel):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        unique_together = (
            "cart",
            "variant",
        )

    def __str__(self):
        return (
            f"{self.variant.product.name}"
            f" ({self.quantity})"
        )

    @property
    def unit_price(self):

        if self.variant.sale_price:
            return self.variant.sale_price

        return self.variant.price

    @property
    def line_total(self):
        return self.unit_price * self.quantity