from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages

from .models import Cart, CartItem

from catalog.models import ProductVariant

def get_cart(request):

    if request.user.is_authenticated:

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

    else:

        session_key = request.session.session_key

        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(
            session_key=session_key
        )

    return cart

def cart_detail_view(request):

    cart = get_cart(request)

    items = cart.items.select_related(
        "variant",
        "variant__product"
    )

    subtotal = Decimal("0.00")

    for item in items:

        price = (
            item.variant.sale_price
            if item.variant.sale_price
            else item.variant.price
        )

        subtotal += price * item.quantity

    context = {
        "cart": cart,
        "items": items,
        "subtotal": subtotal,
    }

    return render(
        request,
        "cart/cart.html",
        context
    )

def add_to_cart_view(request, variant_id):
    if variant.current_stock <= 0:
        messages.error(
            request,
            "Product is out of stock."
        )
        return redirect("product_detail", slug=variant.product.slug)

    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        is_active=True
    )

    cart = get_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            "quantity": 1
        }
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(
        request,
        "Product added to cart."
    )

    return redirect("cart_detail")

def increase_quantity_view(request,item_id):
    if item.quantity < item.variant.current_stock:
        item.quantity += 1
        item.save()

    item = get_object_or_404(
        CartItem,
        id=item_id
    )

    item.quantity += 1
    item.save()

    return redirect("cart_detail")

def decrease_quantity_view(request,item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()

    return redirect("cart_detail")

def remove_cart_item_view(
    request,
    item_id
):

    item = get_object_or_404(
        CartItem,
        id=item_id
    )

    item.delete()

    messages.success(
        request,
        "Item removed."
    )

    return redirect("cart_detail")