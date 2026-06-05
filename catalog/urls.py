from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Brand URLs
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/create/', views.brand_create, name='brand_create'),
    path('brands/<int:pk>/update/', views.brand_update, name='brand_update'),
    path('brands/<int:pk>/delete/', views.brand_delete, name='brand_delete'),
    
    path('attributes/', views.attribute_list, name='attribute_list'),
    path('attributes/create/', views.attribute_create, name='attribute_create'),
    path('attributes/<int:pk>/update/', views.attribute_update, name='attribute_update'),
    path('attributes/<int:pk>/delete/', views.attribute_delete, name='attribute_delete'),
    path('attributes/<int:pk>/', views.attribute_detail, name='attribute_detail'),
    
    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Variant URLs
    path('products/<int:product_pk>/variants/create/', views.variant_create, name='variant_create'),
    path('products/<int:product_pk>/variants/<int:variant_pk>/update/', views.variant_update, name='variant_update'),
    path('products/<int:product_pk>/variants/<int:variant_pk>/delete/', views.variant_delete, name='variant_delete'),

    path('shop/', views.shop_view, name='shop'),
    path('product/<int:pk>/', views.product_detail_customer, name='product_detail_customer'),
    path('product/<int:pk>/<slug:slug>/', views.product_detail_customer, name='product_detail_customer'),
    ]