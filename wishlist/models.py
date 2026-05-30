from django.db import models

from accounts.models import User
from catalog.models import Product

from core.models import BaseModel


class Wishlist(BaseModel):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    def __str__(self):
        return f"{self.user.email} Wishlist"


class WishlistItem(BaseModel):

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )

    class Meta:
        unique_together = (
            "wishlist",
            "product"
        )

    def __str__(self):
        return self.product.name