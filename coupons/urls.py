from django.urls import path

from . import views

urlpatterns = [

    path(
        "apply/",
        views.apply_coupon_view,
        name="apply_coupon"
    ),

    path(
        "remove/",
        views.remove_coupon_view,
        name="remove_coupon"
    ),
]