from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import *

from analytics.models import *


def home_view(request):

    categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    )

    featured_products = Product.objects.filter(
        status="active",
        is_featured=True
    )[:12]

    recently_viewed_ids = request.session.get(
        "recently_viewed_products",
        []
    )

    recently_viewed_products = Product.objects.filter(
        id__in=recently_viewed_ids
    )

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "recently_viewed_products": recently_viewed_products,
    }

    return render(
        request,
        "catalog/home.html",
        context
    )


def category_products_view(request, slug):

    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True
    )

    products = Product.objects.filter(
        category=category,
        status="active"
    )

    CategoryView.objects.create(
        user=request.user if request.user.is_authenticated else None,
        category=category,
        ip_address=request.META.get("REMOTE_ADDR")
    )

    context = {
        "category": category,
        "products": products
    }

    return render(
        request,
        "catalog/category_products.html",
        context
    )


def product_detail_view(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug,
        status="active"
    )

    variants = product.variants.filter(
        is_active=True
    )

    images = product.images.all()

    reviews = product.reviews.filter(
        is_approved=True
    )

    # Product View Tracking
    ProductView.objects.create(
        user=request.user if request.user.is_authenticated else None,
        product=product,
        ip_address=request.META.get("REMOTE_ADDR")
    )

    # Visitor Tracking
    VisitorLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        page_type="product",
        page_id=product.id,
        ip_address=request.META.get("REMOTE_ADDR")
    )

    # Recently Viewed Products
    recently_viewed = request.session.get(
        "recently_viewed_products",
        []
    )

    if product.id in recently_viewed:
        recently_viewed.remove(product.id)

    recently_viewed.insert(0, product.id)

    request.session[
        "recently_viewed_products"
    ] = recently_viewed[:10]

    context = {
        "product": product,
        "variants": variants,
        "images": images,
        "reviews": reviews,
    }

    return render(
        request,
        "catalog/product_detail.html",
        context
    )


def search_view(request):

    query = request.GET.get(
        "q",
        ""
    )

    products = Product.objects.filter(
        status="active"
    )

    if query:

        SearchLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query=query
        )

        products = products.filter(

            Q(name__icontains=query)

            |

            Q(description__icontains=query)

            |

            Q(category__name__icontains=query)

            |

            Q(brand__name__icontains=query)

        ).distinct()

    context = {
        "query": query,
        "products": products
    }

    return render(
        request,
        "catalog/search_results.html",
        context
    )