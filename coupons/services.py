from decimal import Decimal

from django.utils import timezone
def validate_coupon(
    coupon,
    cart_total
):

    now = timezone.now()

    if not coupon.is_active:
        return False, "Coupon inactive"

    if now < coupon.valid_from:
        return False, "Coupon not started"

    if now > coupon.valid_to:
        return False, "Coupon expired"

    if coupon.used_count >= coupon.usage_limit:
        return False, "Coupon usage exceeded"

    if cart_total < coupon.minimum_order_amount:
        return (
            False,
            f"Minimum order amount is ₹{coupon.minimum_order_amount}"
        )

    return True, "Valid"

def calculate_discount(
    coupon,
    subtotal
):

    if coupon.discount_type == "fixed":

        return min(
            coupon.value,
            subtotal
        )

    discount = (
        subtotal
        * coupon.value
        / Decimal("100")
    )

    if coupon.maximum_discount:

        discount = min(
            discount,
            coupon.maximum_discount
        )

    return discount

