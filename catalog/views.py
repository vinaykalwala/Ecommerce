from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from .models import*
from .forms import *

def home_view(request):
    """Home page view"""
    categories = Category.objects.filter(parent__isnull=True, is_active=True)
    featured_products = Product.objects.filter(status="active", is_featured=True)[:12]
    new_products = Product.objects.filter(status="active").order_by('-created_at')[:8]
    
    # Get recently viewed products from session
    recently_viewed_ids = request.session.get("recently_viewed_products", [])
    recently_viewed_products = Product.objects.filter(id__in=recently_viewed_ids, status="active")
    
    context = {
        "categories": categories,
        "featured_products": featured_products,
        "new_products": new_products,
        "recently_viewed_products": recently_viewed_products,
    }
    return render(request, "catalog/home.html", context)


def attribute_list(request):
    """List all attributes with search and pagination"""
    attributes = Attribute.objects.all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        attributes = attributes.filter(name__icontains=search_query)
    
    # Filter by data type
    data_type_filter = request.GET.get('data_type', '')
    if data_type_filter:
        attributes = attributes.filter(data_type=data_type_filter)
    
    # Pagination
    paginator = Paginator(attributes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'data_type_filter': data_type_filter,
        'data_types': Attribute.DATA_TYPES,
    }
    return render(request, 'catalog/attribute/list.html', context)


def attribute_create(request):
    """Create a new attribute"""
    if request.method == 'POST':
        form = AttributeForm(request.POST)
        if form.is_valid():
            attribute = form.save()
            messages.success(request, f'Attribute "{attribute.name}" created successfully.')
            return redirect('catalog:attribute_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttributeForm()
    
    context = {
        'form': form,
        'title': 'Create Attribute',
    }
    return render(request, 'catalog/attribute/form.html', context)


def attribute_update(request, pk):
    """Update an existing attribute"""
    attribute = get_object_or_404(Attribute, pk=pk)
    
    if request.method == 'POST':
        form = AttributeForm(request.POST, instance=attribute)
        if form.is_valid():
            attribute = form.save()
            messages.success(request, f'Attribute "{attribute.name}" updated successfully.')
            return redirect('catalog:attribute_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttributeForm(instance=attribute)
    
    context = {
        'form': form,
        'attribute': attribute,
        'title': 'Update Attribute',
    }
    return render(request, 'catalog/attribute/form.html', context)


def attribute_delete(request, pk):
    """Delete an attribute"""
    if request.method == 'POST':
        attribute = get_object_or_404(Attribute, pk=pk)
        name = attribute.name
        
        # Check if attribute is in use
        if attribute.productattribute_set.exists():
            messages.error(request, f'Cannot delete "{name}" because it is being used by products.')
        elif attribute.variantattribute_set.exists():
            messages.error(request, f'Cannot delete "{name}" because it is being used by variants.')
        else:
            attribute.delete()
            messages.success(request, f'Attribute "{name}" deleted successfully.')
        
        return redirect('catalog:attribute_list')
    
    return redirect('catalog:attribute_list')


def attribute_detail(request, pk):
    """View attribute details and usage"""
    attribute = get_object_or_404(Attribute, pk=pk)
    
    # Get products using this attribute
    products_using = ProductAttribute.objects.filter(attribute=attribute).select_related('product')[:10]
    
    # Get variants using this attribute
    variants_using = VariantAttribute.objects.filter(attribute=attribute).select_related('variant__product')[:10]
    
    context = {
        'attribute': attribute,
        'products_using': products_using,
        'variants_using': variants_using,
        'product_count': attribute.productattribute_set.count(),
        'variant_count': attribute.variantattribute_set.count(),
    }
    return render(request, 'catalog/attribute/detail.html', context)

# Category Views
def category_list(request):
    categories = Category.objects.select_related('parent').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
    
    # Pagination
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'catalog/category/list.html', context)


def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('catalog:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'catalog/category/form.html', {'form': form, 'title': 'Create Category'})


def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('catalog:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'catalog/category/form.html', {'form': form, 'title': 'Update Category', 'category': category})


def category_delete(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully.')
        return redirect('catalog:category_list')
    return redirect('catalog:category_list')


# Brand Views
def brand_list(request):
    brands = Brand.objects.all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        brands = brands.filter(name__icontains=search_query)
    
    # Pagination
    paginator = Paginator(brands, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'catalog/brand/list.html', context)


def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            brand = form.save()
            messages.success(request, f'Brand "{brand.name}" created successfully.')
            return redirect('catalog:brand_list')
    else:
        form = BrandForm()
    
    return render(request, 'catalog/brand/form.html', {'form': form, 'title': 'Create Brand'})


def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            brand = form.save()
            messages.success(request, f'Brand "{brand.name}" updated successfully.')
            return redirect('catalog:brand_list')
    else:
        form = BrandForm(instance=brand)
    
    return render(request, 'catalog/brand/form.html', {'form': form, 'title': 'Update Brand', 'brand': brand})


def brand_delete(request, pk):
    if request.method == 'POST':
        brand = get_object_or_404(Brand, pk=pk)
        name = brand.name
        brand.delete()
        messages.success(request, f'Brand "{name}" deleted successfully.')
        return redirect('catalog:brand_list')
    return redirect('catalog:brand_list')


# Product Views
def product_list(request):
    products = Product.objects.select_related('category', 'brand').prefetch_related('variants').all()
    
    # Search and filters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    brand_filter = request.GET.get('brand', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        products = products.filter(name__icontains=search_query)
    if category_filter:
        products = products.filter(category_id=category_filter)
    if brand_filter:
        products = products.filter(brand_id=brand_filter)
    if status_filter:
        products = products.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'brand_filter': brand_filter,
        'status_filter': status_filter,
        'categories': categories,
        'brands': brands,
        'status_choices': Product.STATUS_CHOICES,
    }
    return render(request, 'catalog/product/list.html', context)


def product_create(request):
    """Create a new product with attributes, images, and variants"""
    
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        attribute_formset = ProductAttributeFormSet(request.POST, request.FILES, prefix='attributes')
        image_formset = ProductImageFormSet(request.POST, request.FILES, prefix='images')
        variant_formset = ProductVariantFormSet(request.POST, request.FILES, prefix='variants')
        
        # Validate all forms
        is_product_valid = product_form.is_valid()
        is_attribute_valid = attribute_formset.is_valid()
        is_image_valid = image_formset.is_valid()
        is_variant_valid = variant_formset.is_valid()
        
        if all([is_product_valid, is_attribute_valid, is_image_valid, is_variant_valid]):
            try:
                with transaction.atomic():
                    # Save product
                    product = product_form.save()
                    
                    # Save attributes
                    attribute_formset.instance = product
                    attribute_formset.save()
                    
                    # Save images
                    image_formset.instance = product
                    image_formset.save()
                    
                    # Save variants
                    variant_formset.instance = product
                    variant_formset.save()
                    
                    messages.success(request, f'Product "{product.name}" created successfully.')
                    
                    if 'save_continue' in request.POST:
                        return redirect('catalog:product_update', pk=product.pk)
                    return redirect('catalog:product_list')
                    
            except Exception as e:
                messages.error(request, f'Error creating product: {str(e)}')
        else:
            # Collect all errors
            if not is_product_valid:
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Product {field}: {error}')
            
            if not is_attribute_valid:
                for form in attribute_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Attribute {field}: {error}')
            
            if not is_image_valid:
                for form in image_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Image {field}: {error}')
            
            if not is_variant_valid:
                for form in variant_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Variant {field}: {error}')
    else:
        product_form = ProductForm()
        attribute_formset = ProductAttributeFormSet(prefix='attributes')
        image_formset = ProductImageFormSet(prefix='images')
        variant_formset = ProductVariantFormSet(prefix='variants')
    
    context = {
        'product_form': product_form,
        'attribute_formset': attribute_formset,
        'image_formset': image_formset,
        'variant_formset': variant_formset,
        'title': 'Create Product',
    }
    return render(request, 'catalog/product/form.html', context)


def product_update(request, pk):
    """Update an existing product with attributes, images, and variants"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        attribute_formset = ProductAttributeFormSet(request.POST, request.FILES, prefix='attributes', instance=product)
        image_formset = ProductImageFormSet(request.POST, request.FILES, prefix='images', instance=product)
        variant_formset = ProductVariantFormSet(request.POST, request.FILES, prefix='variants', instance=product)
        
        # Validate all forms
        is_product_valid = product_form.is_valid()
        is_attribute_valid = attribute_formset.is_valid()
        is_image_valid = image_formset.is_valid()
        is_variant_valid = variant_formset.is_valid()
        
        if all([is_product_valid, is_attribute_valid, is_image_valid, is_variant_valid]):
            try:
                with transaction.atomic():
                    # Save product
                    product = product_form.save()
                    
                    # Save attributes
                    attribute_formset.save()
                    
                    # Save images
                    image_formset.save()
                    
                    # Save variants
                    variant_formset.save()
                    
                    messages.success(request, f'Product "{product.name}" updated successfully.')
                    
                    if 'save_continue' in request.POST:
                        return redirect('catalog:product_update', pk=product.pk)
                    return redirect('catalog:product_list')
                    
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
        else:
            # Collect all errors
            if not is_product_valid:
                for field, errors in product_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Product {field}: {error}')
            
            if not is_attribute_valid:
                for form in attribute_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Attribute {field}: {error}')
            
            if not is_image_valid:
                for form in image_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Image {field}: {error}')
            
            if not is_variant_valid:
                for form in variant_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Variant {field}: {error}')
    else:
        product_form = ProductForm(instance=product)
        attribute_formset = ProductAttributeFormSet(prefix='attributes', instance=product)
        image_formset = ProductImageFormSet(prefix='images', instance=product)
        variant_formset = ProductVariantFormSet(prefix='variants', instance=product)
    
    context = {
        'product_form': product_form,
        'attribute_formset': attribute_formset,
        'image_formset': image_formset,
        'variant_formset': variant_formset,
        'product': product,
        'title': 'Update Product',
    }
    return render(request, 'catalog/product/form.html', context)

def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand')
        .prefetch_related('attributes__attribute', 'images', 'variants'),
        pk=pk
    )
    
    return render(request, 'catalog/product/detail.html', {'product': product})


def product_delete(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
        return redirect('catalog:product_list')
    return redirect('catalog:product_list')


def variant_create(request, product_pk):
    """Create a new variant for a product"""
    product = get_object_or_404(Product, pk=product_pk)
    
    if request.method == 'POST':
        variant_form = ProductVariantForm(request.POST)
        attribute_formset = VariantAttributeFormSet(request.POST, request.FILES, prefix='attributes')
        image_formset = VariantImageFormSet(request.POST, request.FILES, prefix='images')
        
        # Validate all forms
        is_variant_valid = variant_form.is_valid()
        is_attribute_valid = attribute_formset.is_valid()
        is_image_valid = image_formset.is_valid()
        
        if all([is_variant_valid, is_attribute_valid, is_image_valid]):
            try:
                with transaction.atomic():
                    variant = variant_form.save(commit=False)
                    variant.product = product
                    variant.save()
                    
                    attribute_formset.instance = variant
                    attribute_formset.save()
                    
                    image_formset.instance = variant
                    image_formset.save()
                    
                    messages.success(request, f'Variant "{variant.sku}" created successfully.')
                    return redirect('catalog:product_detail', pk=product.pk)
                    
            except Exception as e:
                messages.error(request, f'Error creating variant: {str(e)}')
        else:
            # Collect all errors
            if not is_variant_valid:
                for field, errors in variant_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Variant {field}: {error}')
            
            if not is_attribute_valid:
                for form in attribute_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Attribute {field}: {error}')
            
            if not is_image_valid:
                for form in image_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Image {field}: {error}')
    else:
        variant_form = ProductVariantForm()
        attribute_formset = VariantAttributeFormSet(prefix='attributes')
        image_formset = VariantImageFormSet(prefix='images')
    
    context = {
        'variant_form': variant_form,
        'attribute_formset': attribute_formset,
        'image_formset': image_formset,
        'product': product,
        'title': 'Create Variant',
    }
    return render(request, 'catalog/product/variant_form.html', context)


def variant_update(request, product_pk, variant_pk):
    """Update an existing variant"""
    product = get_object_or_404(Product, pk=product_pk)
    variant = get_object_or_404(ProductVariant, pk=variant_pk, product=product)
    
    if request.method == 'POST':
        variant_form = ProductVariantForm(request.POST, instance=variant)
        attribute_formset = VariantAttributeFormSet(request.POST, request.FILES, prefix='attributes', instance=variant)
        image_formset = VariantImageFormSet(request.POST, request.FILES, prefix='images', instance=variant)
        
        # Validate all forms
        is_variant_valid = variant_form.is_valid()
        is_attribute_valid = attribute_formset.is_valid()
        is_image_valid = image_formset.is_valid()
        
        if all([is_variant_valid, is_attribute_valid, is_image_valid]):
            try:
                with transaction.atomic():
                    variant_form.save()
                    attribute_formset.save()
                    image_formset.save()
                    
                    messages.success(request, f'Variant "{variant.sku}" updated successfully.')
                    return redirect('catalog:product_detail', pk=product.pk)
                    
            except Exception as e:
                messages.error(request, f'Error updating variant: {str(e)}')
        else:
            # Collect all errors
            if not is_variant_valid:
                for field, errors in variant_form.errors.items():
                    for error in errors:
                        messages.error(request, f'Variant {field}: {error}')
            
            if not is_attribute_valid:
                for form in attribute_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Attribute {field}: {error}')
            
            if not is_image_valid:
                for form in image_formset:
                    if form.errors:
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f'Image {field}: {error}')
    else:
        variant_form = ProductVariantForm(instance=variant)
        attribute_formset = VariantAttributeFormSet(prefix='attributes', instance=variant)
        image_formset = VariantImageFormSet(prefix='images', instance=variant)
    
    context = {
        'variant_form': variant_form,
        'attribute_formset': attribute_formset,
        'image_formset': image_formset,
        'product': product,
        'variant': variant,
        'title': 'Update Variant',
    }
    return render(request, 'catalog/product/variant_form.html', context)

def variant_delete(request, product_pk, variant_pk):
    if request.method == 'POST':
        variant = get_object_or_404(ProductVariant, pk=variant_pk, product_id=product_pk)
        sku = variant.sku
        variant.delete()
        messages.success(request, f'Variant "{sku}" deleted successfully.')
        return redirect('catalog:product_detail', pk=product_pk)
    return redirect('catalog:product_detail', pk=product_pk)

# Add to catalog/views.py

from django.db.models import Q, Count, Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def shop_view(request):
    """Customer-facing shop page with filtering and sorting"""
    
    # Base queryset
    products = Product.objects.filter(status='active').select_related(
        'category', 'brand'
    ).prefetch_related('images', 'variants')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Filter by brand
    brand_slug = request.GET.get('brand')
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(variants__price__gte=min_price)
    if max_price:
        products = products.filter(variants__price__lte=max_price)
    
    # Filter by sale items
    on_sale = request.GET.get('on_sale')
    if on_sale == 'true':
        products = products.filter(variants__sale_price__isnull=False)
    
    # Filter by stock status
    in_stock = request.GET.get('in_stock')
    if in_stock == 'true':
        products = products.filter(variants__current_stock__gt=0)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = {
        'price_asc': 'variants__price',
        'price_desc': '-variants__price',
        'name_asc': 'name',
        'name_desc': '-name',
        'created_desc': '-created_at',
        'created_asc': 'created_at',
    }
    products = products.order_by(valid_sorts.get(sort_by, '-created_at')).distinct()
    
    # Get price range for filter
    price_range = ProductVariant.objects.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Get all categories with product counts
    categories = Category.objects.filter(
        is_active=True,
        products__status='active'
    ).annotate(
        product_count=Count('products', filter=Q(products__status='active'))
    ).order_by('name')
    
    # Get all brands with product counts
    brands = Brand.objects.filter(
        is_active=True,
        products__status='active'
    ).annotate(
        product_count=Count('products', filter=Q(products__status='active'))
    ).order_by('name')
    
    context = {
        'products': products_page,
        'categories': categories,
        'brands': brands,
        'search_query': search_query,
        'sort_by': sort_by,
        'selected_category': category_slug,
        'selected_brand': brand_slug,
        'min_price': min_price,
        'max_price': max_price,
        'on_sale': on_sale,
        'in_stock': in_stock,
        'price_range': price_range,
    }
    return render(request, 'catalog/shop.html', context)


def product_detail_customer(request, pk, slug=None):
    """Customer-facing product detail page"""
    
    # Get product with all related data
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand')
        .prefetch_related(
            'attributes__attribute',
            'images',
            'variants__attributes__attribute',
            'variants__images',
            'category__products',
            'brand__products'
        ),
        pk=pk,
        status='active'
    )
    
    # Add to recently viewed session
    recently_viewed = request.session.get('recently_viewed', [])
    if pk not in recently_viewed:
        recently_viewed.insert(0, pk)
        if len(recently_viewed) > 10:
            recently_viewed.pop()
        request.session['recently_viewed'] = recently_viewed
    
    # Get active variants
    variants = product.variants.filter(is_active=True)
    
    # Get minimum price for display
    min_price = variants.aggregate(Min('price'))['price__min'] if variants else product.variants.first().price
    
    # Check if product has variants with sale price
    has_sale = variants.filter(sale_price__isnull=False).exists()
    
    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        status='active'
    ).exclude(
        id=product.id
    ).select_related('category', 'brand').prefetch_related('images', 'variants')[:8]
    
    # Get products from same brand
    brand_products = None
    if product.brand:
        brand_products = Product.objects.filter(
            brand=product.brand,
            status='active'
        ).exclude(
            id=product.id
        ).select_related('category', 'brand').prefetch_related('images', 'variants')[:4]
    
    # Group attributes for display
    attributes = []
    for attr in product.attributes.select_related('attribute').all():
        attributes.append({
            'name': attr.attribute.name,
            'value': attr.value,
            'data_type': attr.attribute.data_type
        })
    
    # Get product images
    images = product.images.all()
    main_image = images.filter(is_primary=True).first() or images.first()
    
    # Prepare variant data for JSON (for dynamic variant selection)
    variant_data = []
    for variant in variants:
        variant_data.append({
            'id': variant.id,
            'sku': variant.sku,
            'price': float(variant.price),
            'sale_price': float(variant.sale_price) if variant.sale_price else None,
            'final_price': float(variant.final_price),
            'stock': variant.current_stock,
            'in_stock': variant.in_stock,
            'attributes': [
                {'name': attr.attribute.name, 'value': attr.value}
                for attr in variant.attributes.select_related('attribute').all()
            ],
            'images': [
                {'url': img.image.url, 'alt': img.alt_text}
                for img in variant.images.all()
            ]
        })
    
    context = {
        'product': product,
        'variants': variants,
        'min_price': min_price,
        'has_sale': has_sale,
        'attributes': attributes,
        'images': images,
        'main_image': main_image,
        'related_products': related_products,
        'brand_products': brand_products,
        'variant_data': variant_data,
    }
    return render(request, 'catalog/product_detail_customer.html', context)