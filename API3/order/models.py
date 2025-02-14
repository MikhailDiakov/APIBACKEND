from django.db import models
from decimal import Decimal


class Order(models.Model):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ORDER_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]
    cart_key = models.CharField(max_length=255, unique=True)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    status = models.CharField(
        max_length=10, choices=ORDER_STATUS_CHOICES, default=PENDING
    )
    is_paid = models.BooleanField(default=False)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(0))
    price_after_discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    price_per_item = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    image = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"OrderItem {self.id} - {self.name}"
