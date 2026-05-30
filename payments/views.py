from django.conf import settings

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.http import JsonResponse

from django.utils import timezone

from .models import Payment

from .services import client

from orders.models import Order

from inventory.models import InventoryLog

@login_required
def create_payment_view(
    request,
    order_id
):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    amount = int(
        order.total * 100
    )

    razorpay_order = client.order.create(
        {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,
        }
    )

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "amount": order.total,
            "razorpay_order_id":
                razorpay_order["id"]
        }
    )

    context = {

        "order": order,

        "payment": payment,

        "razorpay_key":
            settings.RAZORPAY_KEY_ID,

        "amount": amount,
    }

    return render(
        request,
        "payments/payment.html",
        context
    )

@login_required
def verify_payment_view(request):

    if request.method != "POST":
        return JsonResponse(
            {"success": False}
        )
    razorpay_payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    razorpay_order_id = request.POST.get(
        "razorpay_order_id"
    )

    razorpay_signature = request.POST.get(
        "razorpay_signature"
    )
    try:

        client.utility.verify_payment_signature(
            {
                "razorpay_order_id":
                    razorpay_order_id,

                "razorpay_payment_id":
                    razorpay_payment_id,

                "razorpay_signature":
                    razorpay_signature,
            }
        )

    except:

        return JsonResponse(
            {"success": False}
        )
    payment = Payment.objects.get(
        razorpay_order_id=
        razorpay_order_id
    )

    payment.razorpay_payment_id = (
        razorpay_payment_id
    )

    payment.transaction_id = (
        razorpay_payment_id
    )

    payment.status = "success"

    payment.paid_at = timezone.now()
    if cart.coupon:

        coupon = cart.coupon

        coupon.used_count += 1

        coupon.save()

    payment.save()
    order = payment.order

    order.status = "paid"

    order.save()
    for item in order.items.all():

        variant = item.variant

        variant.current_stock -= (
            item.quantity
        )

        variant.save()
        InventoryLog.objects.create(

            variant=variant,

            quantity=item.quantity,

            action="order_placed"
        )
    cart = request.user.cart

    cart.items.all().delete()

    cart.coupon = None

    cart.save()
    return JsonResponse(
        {
            "success": True,
            "order_id": order.id
        }
    )