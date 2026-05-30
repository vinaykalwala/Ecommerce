from orders.models import OrderItem
def can_review_product(
    user,
    product
):

    return OrderItem.objects.filter(

        order__user=user,

        order__status="delivered",

        variant__product=product

    ).exists()

