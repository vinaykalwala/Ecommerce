from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.home_view,
        name="home"
    ),

    path(
        "search/",
        views.search_view,
        name="search"
    ),

    path(
        "category/<slug:slug>/",
        views.category_products_view,
        name="category_products"
    ),

    path(
        "product/<slug:slug>/",
        views.product_detail_view,
        name="product_detail"
    ),
]