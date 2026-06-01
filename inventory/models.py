from core.models import *
from catalog.models import *

class InventoryLog(BaseModel):

    ACTIONS = (
        ("stock_added", "Stock Added"),
        ("stock_removed", "Stock Removed"),
        ("order_placed", "Order Placed"),
        ("order_cancelled", "Order Cancelled"),
        ("return_received", "Return Received"),
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="inventory_logs"
    )

    quantity = models.IntegerField()

    action = models.CharField(
        max_length=50,
        choices=ACTIONS
    )

    remarks = models.CharField(
        max_length=255,
        blank=True
    )