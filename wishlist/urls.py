from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.wishlist_view,
        name="wishlist"
    ),

    path(
        "add/<int:product_id>/",
        views.add_to_wishlist_view,
        name="add_to_wishlist"
    ),

    path(
        "remove/<int:item_id>/",
        views.remove_from_wishlist_view,
        name="remove_from_wishlist"
    ),
]