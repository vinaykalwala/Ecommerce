from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Wishlist,
    WishlistItem
)

from catalog.models import Product

@login_required
def wishlist_view(request):

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )

    context = {
        "wishlist": wishlist,
        "items": wishlist.items.select_related(
            "product"
        )
    }

    return render(
        request,
        "wishlist/wishlist.html",
        context
    )

@login_required
def add_to_wishlist_view(
    request,
    product_id
):

    product = get_object_or_404(
        Product,
        id=product_id,
        status="active"
    )

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )

    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )

    if created:

        messages.success(
            request,
            "Added to wishlist."
        )

    else:

        messages.info(
            request,
            "Already in wishlist."
        )

    return redirect(
        "product_detail",
        slug=product.slug
    )

@login_required
def remove_from_wishlist_view(
    request,
    item_id
):

    item = get_object_or_404(
        WishlistItem,
        id=item_id,
        wishlist__user=request.user
    )

    item.delete()

    messages.success(
        request,
        "Removed from wishlist."
    )

    return redirect("wishlist")

