from uuid import uuid4

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import Address

from cart.models import Cart

from .models import (
    Order,
    OrderItem,
    OrderAddress
)

@login_required
def checkout_view(request):

    cart = request.user.cart

    addresses = request.user.addresses.all()

    if not cart.items.exists():

        messages.error(
            request,
            "Your cart is empty."
        )

        return redirect("cart_detail")

    context = {
        "cart": cart,
        "addresses": addresses,
    }

    return render(
        request,
        "orders/checkout.html",
        context
    )

@login_required
def place_order_view(request):

    if request.method != "POST":
        return redirect("checkout")

    cart = request.user.cart

    address_id = request.POST.get(
        "address"
    )

    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    order = Order.objects.create(

        user=request.user,

        order_number=str(uuid4())[:12],

        subtotal=cart.subtotal,

        discount=cart.discount_amount,

        total=cart.total,

        status="payment_pending"
    )
    OrderAddress.objects.create(

        order=order,

        full_name=address.full_name,

        mobile_number=address.mobile_number,

        address_line_1=address.address_line_1,

        address_line_2=address.address_line_2,

        city=address.city,

        state=address.state,

        country=address.country,

        postal_code=address.postal_code
    )
    
    for item in cart.items.all():

        price = item.unit_price

        OrderItem.objects.create(

            order=order,

            variant=item.variant,

            product_name=item.variant.product.name,

            sku=item.variant.sku,

            quantity=item.quantity,

            price=price,

            total=price * item.quantity
        )
    return redirect(
        "create_payment",
        order_id=order.id
    )

@login_required
def order_success_view(
    request,
    order_id
):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/order_success.html",
        {"order": order}
    )

@login_required
def my_orders_view(request):

    orders = request.user.orders.all()

    return render(
        request,
        "orders/my_orders.html",
        {"orders": orders}
    )

@login_required
def order_detail_view(
    request,
    order_id
):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "orders/order_detail.html",
        {"order": order}
    )

@login_required
def cancel_order_view(
    request,
    order_id
):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.status in [
        "pending",
        "payment_pending",
        "paid"
    ]:

        order.status = "cancelled"
        order.save()

    return redirect(
        "order_detail",
        order.id
    )

