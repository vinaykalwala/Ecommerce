from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from core.models import BaseModel
import uuid


class Category(BaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)

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

    is_active = models.BooleanField(
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class Brand(BaseModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)

    logo = models.ImageField(
        upload_to="brands/",
        blank=True,
        null=True
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(
        default=True,
        db_index=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class Product(BaseModel):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    name = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        blank=True,
        db_index=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        db_index=True
    )

    is_featured = models.BooleanField(
        default=False,
        db_index=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        if hasattr(self, "reviews"):
            reviews = self.reviews.filter(is_approved=True)

            if reviews.exists():
                return round(
                    sum(review.rating for review in reviews)
                    / reviews.count(),
                    1
                )

        return 0

    @property
    def review_count(self):
        if hasattr(self, "reviews"):
            return self.reviews.filter(
                is_approved=True
            ).count()

        return 0

    @property
    def main_image(self):
        return (
            self.images.filter(
                is_primary=True
            ).first()
            or self.images.first()
        )


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

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


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

    class Meta:
        unique_together = ["product", "attribute"]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.attribute.name}: "
            f"{self.value}"
        )


class ProductVariant(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    current_stock = models.PositiveIntegerField(
        default=0
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=5
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True
    )

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

    def clean(self):
        if (
            self.sale_price and
            self.sale_price > self.price
        ):
            raise ValidationError(
                "Sale price cannot exceed price."
            )

    @property
    def final_price(self):
        return self.sale_price or self.price

    @property
    def in_stock(self):
        return self.current_stock > 0

    @property
    def is_low_stock(self):
        return (
            self.current_stock <=
            self.low_stock_threshold
        )

    @property
    def stock_status(self):
        if self.current_stock > 10:
            return "In Stock"

        elif self.current_stock > 0:
            return f"Only {self.current_stock} left"

        return "Out of Stock"

    def add_stock(self, quantity):
        self.current_stock += quantity
        self.save(update_fields=["current_stock"])

    def reduce_stock(self, quantity):
        if quantity > self.current_stock:
            raise ValidationError(
                "Insufficient stock."
            )

        self.current_stock -= quantity
        self.save(update_fields=["current_stock"])


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

    class Meta:
        unique_together = ["variant", "attribute"]

    def __str__(self):
        return (
            f"{self.variant.sku} - "
            f"{self.attribute.name}: "
            f"{self.value}"
        )


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/%Y/%m/%d/"
    )

    is_primary = models.BooleanField(
        default=False
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = [
            "-is_primary",
            "sort_order",
            "created_at"
        ]

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product
            ).exclude(
                pk=self.pk
            ).update(
                is_primary=False
            )


class VariantImage(BaseModel):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="variants/%Y/%m/%d/"
    )

    is_primary = models.BooleanField(
        default=False
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = [
            "-is_primary",
            "sort_order",
            "created_at"
        ]

    def __str__(self):
        return f"Image for {self.variant.sku}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_primary:
            VariantImage.objects.filter(
                variant=self.variant
            ).exclude(
                pk=self.pk
            ).update(
                is_primary=False
            )