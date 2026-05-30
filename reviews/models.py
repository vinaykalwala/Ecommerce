from django.db import models

from accounts.models import User
from catalog.models import Product

from core.models import BaseModel


class Review(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField()

    title = models.CharField(
        max_length=255
    )

    review = models.TextField()

    is_verified_purchase = models.BooleanField(
        default=False
    )

    is_approved = models.BooleanField(
        default=True
    )

    class Meta:

        unique_together = (
            "user",
            "product"
        )

    def __str__(self):
        return (
            f"{self.product.name} "
            f"- {self.rating}"
        )

class ReviewImage(BaseModel):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="review_images/"
    )