from rest_framework import serializers
from .models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    sell_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )

    class Meta:
        model = Product
        fields = "__all__"

    def validate(self, data):
        price = data.get("price")
        discount = data.get("discount")
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        category = data.get("category")
        image = data.get("image")
        available = data.get("available")

        if price is not None and price <= 0:
            raise serializers.ValidationError(
                {"price": "Price must be greater than 0."}
            )

        if discount is not None and (discount < 0 or discount > 100):
            raise serializers.ValidationError(
                {"discount": "Discount must be between 0 and 100."}
            )

        if Product.objects.filter(name=name, category=category).exists():
            raise serializers.ValidationError(
                {"name": "A product with this name already exists in this category."}
            )

        if not name:
            raise serializers.ValidationError({"name": "Product name cannot be empty."})

        if description and len(description) > 1000:
            raise serializers.ValidationError(
                {"description": "Description cannot exceed 1000 characters."}
            )

        if category and not Category.objects.filter(id=category.id).exists():
            raise serializers.ValidationError(
                {"category": "The specified category does not exist."}
            )

        if image:
            valid_extensions = ["jpg", "jpeg", "png"]
            ext = image.name.split(".")[-1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError(
                    {"image": "Only JPG and PNG images are allowed."}
                )

        if not available and price is not None:
            raise serializers.ValidationError(
                {
                    "available": "If the product is unavailable, the price should not be specified."
                }
            )

        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
