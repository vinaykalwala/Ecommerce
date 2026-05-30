from django.db.models import Sum

from orders.models import Order

def total_revenue():

    return (
        Order.objects.filter(
            status__in=[
                "paid",
                "delivered"
            ]
        )
        .aggregate(
            total=Sum("total")
        )
        .get("total")
        or 0
    )

def total_orders():

    return Order.objects.count()

def delivered_orders():

    return Order.objects.filter(
        status="delivered"
    ).count()

def cancelled_orders():

    return Order.objects.filter(
        status="cancelled"
    ).count()

from django.db.models import Sum

from orders.models import OrderItem

def top_products():

    return (

        OrderItem.objects

        .values(
            "product_name"
        )

        .annotate(
            sold=Sum("quantity")
        )

        .order_by("-sold")[:10]

    )

from catalog.models import Product

def top_categories():

    return (

        Product.objects

        .values(
            "category__name"
        )

        .annotate(
            count=Sum(
                "variants__orderitem__quantity"
            )
        )

        .order_by("-count")[:10]

    )

from django.db.models import Count

from .models import ProductView
def most_viewed_products():

    return (

        ProductView.objects

        .values(
            "product__name"
        )

        .annotate(
            views=Count("id")
        )

        .order_by("-views")[:10]

    )

from .models import SearchLog
def popular_searches():

    from django.db.models import Count

    return (

        SearchLog.objects

        .values("query")

        .annotate(
            total=Count("id")
        )

        .order_by("-total")[:20]

    )

