from django.shortcuts import render

from .services import (
    total_revenue,
    total_orders,
    delivered_orders,
    cancelled_orders,
    top_products,
    top_categories,
    most_viewed_products,
    popular_searches
)
def analytics_dashboard_view(
    request
):

    context = {

        "total_revenue":
            total_revenue(),

        "total_orders":
            total_orders(),

        "delivered_orders":
            delivered_orders(),

        "cancelled_orders":
            cancelled_orders(),

        "top_products":
            top_products(),

        "top_categories":
            top_categories(),

        "most_viewed":
            most_viewed_products(),

        "popular_searches":
            popular_searches(),
    }

    return render(
        request,
        "analytics/dashboard.html",
        context
    )

