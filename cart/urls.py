from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.cart_detail_view,
        name="cart_detail"
    ),

    path(
        "add/<int:variant_id>/",
        views.add_to_cart_view,
        name="add_to_cart"
    ),

    path(
        "increase/<int:item_id>/",
        views.increase_quantity_view,
        name="increase_quantity"
    ),

    path(
        "decrease/<int:item_id>/",
        views.decrease_quantity_view,
        name="decrease_quantity"
    ),

    path(
        "remove/<int:item_id>/",
        views.remove_cart_item_view,
        name="remove_cart_item"
    ),
]