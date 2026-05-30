from django.shortcuts import (
    redirect
)

from django.contrib import messages

from .models import Coupon

from .services import (
    validate_coupon
)
def apply_coupon_view(request):

    if request.method != "POST":
        return redirect("cart_detail")

    code = request.POST.get(
        "coupon_code"
    )

    cart = request.user.cart

    try:

        coupon = Coupon.objects.get(
            code=code
        )

    except Coupon.DoesNotExist:

        messages.error(
            request,
            "Invalid coupon code."
        )

        return redirect(
            "cart_detail"
        )

    valid, message = validate_coupon(
        coupon,
        cart.subtotal
    )

    if not valid:

        messages.error(
            request,
            message
        )

        return redirect(
            "cart_detail"
        )

    cart.coupon = coupon

    cart.save()

    messages.success(
        request,
        "Coupon applied successfully."
    )

    return redirect(
        "cart_detail"
    )

def remove_coupon_view(
    request
):

    cart = request.user.cart

    cart.coupon = None

    cart.save()

    messages.success(
        request,
        "Coupon removed."
    )

    return redirect(
        "cart_detail"
    )

