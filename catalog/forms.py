from django import forms
from django.forms import inlineformset_factory
from .models import (
    Category, Brand, Product, ProductAttribute, 
    ProductImage, ProductVariant, VariantAttribute, 
    VariantImage, Attribute
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'image', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'logo', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand Name'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'description', 'status', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['attribute', 'value']
        widgets = {
            'attribute': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Value'}),
        }
    
    def clean(self):
        """Ensure attribute and value are provided together"""
        cleaned_data = super().clean()
        attribute = cleaned_data.get('attribute')
        value = cleaned_data.get('value')
        
        if attribute and not value:
            self.add_error('value', 'Please enter a value for this attribute.')
        
        return cleaned_data


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary', 'sort_order', 'alt_text']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sort Order'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alt Text'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        
        if self.instance.pk or image:
            # Either existing image or new image is fine
            pass
        elif not image and not self.instance.pk:
            self.add_error('image', 'Please select an image file.')
        
        return cleaned_data


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['sku', 'price', 'sale_price', 'current_stock', 'low_stock_threshold', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SKU'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sale Price', 'step': '0.01'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Current Stock'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Low Stock Threshold'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        sale_price = cleaned_data.get('sale_price')
        sku = cleaned_data.get('sku')
        
        if not sku:
            self.add_error('sku', 'SKU is required.')
        
        if price and price <= 0:
            self.add_error('price', 'Price must be greater than 0.')
        
        if sale_price and sale_price > price:
            self.add_error('sale_price', 'Sale price cannot be greater than regular price.')
        
        return cleaned_data


class VariantAttributeForm(forms.ModelForm):
    class Meta:
        model = VariantAttribute
        fields = ['attribute', 'value']
        widgets = {
            'attribute': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Value'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        attribute = cleaned_data.get('attribute')
        value = cleaned_data.get('value')
        
        if attribute and not value:
            self.add_error('value', 'Please enter a value for this attribute.')
        
        return cleaned_data


class VariantImageForm(forms.ModelForm):
    class Meta:
        model = VariantImage
        fields = ['image', 'is_primary', 'sort_order', 'alt_text']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sort Order'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alt Text'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        
        if self.instance.pk or image:
            pass
        elif not image and not self.instance.pk:
            self.add_error('image', 'Please select an image file.')
        
        return cleaned_data


class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ['name', 'data_type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Color, Size, Material'
            }),
            'data_type': forms.Select(attrs={'class': 'form-control'}),
        }


# Formsets with proper configuration
ProductAttributeFormSet = inlineformset_factory(
    Product, 
    ProductAttribute,
    form=ProductAttributeForm,
    extra=1,
    can_delete=True,
    validate_min=False
)

ProductImageFormSet = inlineformset_factory(
    Product, 
    ProductImage,
    form=ProductImageForm,
    extra=1,
    can_delete=True,
    validate_min=False
)

ProductVariantFormSet = inlineformset_factory(
    Product, 
    ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True,
    validate_min=False
)

VariantAttributeFormSet = inlineformset_factory(
    ProductVariant, 
    VariantAttribute,
    form=VariantAttributeForm,
    extra=1,
    can_delete=True,
    validate_min=False
)

VariantImageFormSet = inlineformset_factory(
    ProductVariant, 
    VariantImage,
    form=VariantImageForm,
    extra=1,
    can_delete=True,
    validate_min=False
)