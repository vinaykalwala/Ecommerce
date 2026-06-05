from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    
    # Inventory List and Management
    path('list/', views.inventory_list_view, name='inventory_list'),
    path('detail/<int:variant_id>/', views.inventory_detail_view, name='inventory_detail'),
    path('adjust/<int:variant_id>/', views.inventory_adjust_view, name='inventory_adjust'),
    path('bulk-update/', views.bulk_inventory_update_view, name='bulk_inventory_update'),
    
    # Reports
    path('low-stock/', views.low_stock_report_view, name='low_stock_report'),
    path('logs/', views.inventory_logs_view, name='inventory_logs'),
    path('movement-report/', views.stock_movement_report_view, name='stock_movement_report'),
    
    # Export
    path('export/csv/', views.export_inventory_csv, name='export_inventory_csv'),
    
    # API Endpoints
    path('api/stock/<int:variant_id>/', views.api_get_variant_stock, name='api_get_variant_stock'),
    path('api/bulk-stock-check/', views.api_bulk_stock_check, name='api_bulk_stock_check'),
]