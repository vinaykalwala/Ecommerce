from django.db import models
from core.models import BaseModel
from catalog.models import ProductVariant

class InventoryLog(BaseModel):
    ACTIONS = (
        ("stock_added", "Stock Added"),
        ("stock_removed", "Stock Removed"),
        ("order_placed", "Order Placed"),
        ("order_cancelled", "Order Cancelled"),
        ("return_received", "Return Received"),
        ("stock_adjusted", "Stock Adjusted"),
    )
    
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="inventory_logs")
    quantity = models.IntegerField()
    action = models.CharField(max_length=50, choices=ACTIONS)
    remarks = models.CharField(max_length=255, blank=True)
    previous_stock = models.PositiveIntegerField(default=0)
    new_stock = models.PositiveIntegerField(default=0)
    reference_id = models.CharField(max_length=100, blank=True)  # Order ID or reference
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.variant.sku} - {self.action}: {self.quantity}"