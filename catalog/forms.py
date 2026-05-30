from django import forms

from .models import (
    Category,
    Brand,
    Product,
    ProductVariant,
    ProductImage
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = "__all__"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = "__all__"


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = "__all__"