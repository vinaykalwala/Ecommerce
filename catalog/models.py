from django.db import models
from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=150)

    slug = models.SlugField(unique=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)


class Brand(BaseModel):
    name = models.CharField(max_length=150)

    slug = models.SlugField(unique=True)

    logo = models.ImageField(
        upload_to="brands/",
        blank=True,
        null=True
    )


class Product(BaseModel):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    is_featured = models.BooleanField(default=False)
    @property
    def average_rating(self):

        reviews = self.reviews.filter(
            is_approved=True
        )

        if not reviews.exists():
            return 0

        return round(

            sum(
                review.rating
                for review in reviews
            )

            / reviews.count(),

            1
        )
    @property
    def review_count(self):

        return self.reviews.filter(
            is_approved=True
        ).count()


class Attribute(BaseModel):

    DATA_TYPES = (
        ("text", "Text"),
        ("number", "Number"),
        ("boolean", "Boolean"),
    )

    name = models.CharField(max_length=100)

    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPES
    )


class ProductAttribute(BaseModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attributes"
    )

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE
    )

    value = models.CharField(max_length=255)


class ProductVariant(BaseModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    sku = models.CharField(
        max_length=100,
        unique=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    current_stock = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

class VariantAttribute(BaseModel):

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="attributes"
    )

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE
    )

    value = models.CharField(max_length=255)


class ProductImage(BaseModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    is_primary = models.BooleanField(default=False)