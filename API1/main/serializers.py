from rest_framework import serializers
from .models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    sell_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )

    class Meta:
        model = Product
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
