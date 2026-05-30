from django.urls import path

from . import views

urlpatterns = [

    path(
        "checkout/",
        views.checkout_view,
        name="checkout"
    ),

    path(
        "place-order/",
        views.place_order_view,
        name="place_order"
    ),

    path(
        "success/<int:order_id>/",
        views.order_success_view,
        name="order_success"
    ),

    path(
        "my-orders/",
        views.my_orders_view,
        name="my_orders"
    ),

    path(
        "<int:order_id>/",
        views.order_detail_view,
        name="order_detail"
    ),

    path(
        "<int:order_id>/cancel/",
        views.cancel_order_view,
        name="cancel_order"
    ),
]