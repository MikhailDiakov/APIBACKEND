import redis
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.conf import settings
from datetime import timedelta
import requests
import json
import uuid
from decimal import Decimal
from rest_framework.permissions import BasePermission

PRODUCT_SERVICE = "http://127.0.0.1:8000/api/v1/product/"

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True
)


class MicroservicePermission(BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get("X-MICROSERVICE-API-KEY")
        return api_key == settings.MICROSERVICE_API_KEY


class CartViewSet(viewsets.ViewSet):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if not request.user.is_authenticated:
            if "cart_token" not in request.session:
                request.session["cart_token"] = uuid.uuid4().hex[:16]
                request.session.modified = True

        self.cart_key = (
            f"cart_{request.user.id}"
            if request.user.is_authenticated
            else f"cart_{request.session.get('cart_token', 'default_guest')}"
        )

        self.cart_ttl = (
            timedelta(days=7)
            if request.user.is_authenticated
            else timedelta(minutes=30)
        )

    def get_product_info(self, product_id):
        url = f"{PRODUCT_SERVICE}{product_id}/"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None

    @action(detail=False, methods=["get"])
    def get_cart(self, request):
        cart_data = redis_client.hgetall(self.cart_key)

        cart_data = {
            key.decode("utf-8") if isinstance(key, bytes) else key: json.loads(
                value.decode("utf-8") if isinstance(value, bytes) else value
            )
            for key, value in cart_data.items()
        }

        total_price = Decimal(0)
        cart_details = []

        for product_id, product_data in cart_data.items():
            quantity = int(product_data["quantity"])
            price = Decimal(product_data["price"])
            discount = Decimal(product_data["discount"])
            price_after_discount = price * (1 - discount / 100)
            price_per_item = price_after_discount * quantity

            total_price += price_per_item

            cart_details.append(
                {
                    "product_id": product_id,
                    "name": product_data["name"],
                    "price": price,
                    "discount": discount,
                    "quantity": quantity,
                    "image": product_data["image"],
                    "price_after_discount": price_after_discount,
                    "price_per_item": price_per_item,
                }
            )
        total_price = str(total_price)

        return Response(
            {
                "cart_details": cart_details,
                "total_price": total_price,
                "cart_key": self.cart_key,
            }
        )

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        if not product_id:
            return Response(
                {"error": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be a positive integer.")
        except (ValueError, TypeError):
            return Response(
                {"error": "Quantity must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product_info = self.get_product_info(product_id)
        if not product_info:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        price = Decimal(product_info["price"])
        discount = Decimal(product_info["discount"])
        price_after_discount = price * (1 - discount / 100)

        existing_item = redis_client.hget(self.cart_key, product_id)
        if existing_item:
            existing_item = json.loads(existing_item)
            existing_item["quantity"] += quantity
            redis_client.hset(self.cart_key, product_id, json.dumps(existing_item))
        else:
            cart_item = {
                "quantity": quantity,
                "name": product_info["name"],
                "price": str(price),
                "discount": str(discount),
                "price_after_discount": str(price_after_discount),
                "image": product_info["image"],
            }
            redis_client.hset(self.cart_key, product_id, json.dumps(cart_item))

        redis_client.expire(self.cart_key, int(self.cart_ttl.total_seconds()))

        return Response(
            {
                "message": "Item added to cart",
                "product_id": product_id,
                "quantity": quantity,
                "name": product_info["name"],
                "price": product_info["price"],
                "discount": product_info["discount"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["delete"])
    def remove_item(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"error": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        redis_client.hdel(self.cart_key, product_id)

        if redis_client.hlen(self.cart_key) > 0:
            redis_client.expire(self.cart_key, int(self.cart_ttl.total_seconds()))

        return Response(
            {
                "message": "Item removed from cart",
                "product_id": product_id,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["delete"])
    def clear_cart(self, request):
        redis_client.delete(self.cart_key)

        return Response(
            {
                "message": "Cart cleared",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["patch"])
    def update_quantity(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")
        change = request.data.get("change")

        if not product_id:
            return Response(
                {"error": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_item = redis_client.hget(self.cart_key, product_id)
        if not existing_item:
            return Response(
                {"error": "Product not found in cart."},
                status=status.HTTP_404_NOT_FOUND,
            )

        existing_item = json.loads(existing_item)

        if quantity is not None and change is not None:
            return Response(
                {"error": "You can only provide one of 'quantity' or 'change'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if change is not None:
            try:
                change = int(change)
                existing_item["quantity"] += change

                if existing_item["quantity"] <= 0:
                    return Response(
                        {"error": "Quantity must be greater than 0."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except (ValueError, TypeError):
                return Response(
                    {"error": "Change must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif quantity is not None:
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError("Quantity must be a positive integer.")
                existing_item["quantity"] = quantity

            except (ValueError, TypeError):
                return Response(
                    {"error": "Quantity must be a positive integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        redis_client.hset(self.cart_key, product_id, json.dumps(existing_item))
        redis_client.expire(self.cart_key, int(self.cart_ttl.total_seconds()))

        return Response(
            {
                "message": "Quantity updated successfully.",
                "product_id": product_id,
                "new_quantity": existing_item["quantity"],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def get_user_cart(self, request):
        permission = MicroservicePermission()
        if not permission.has_permission(request, self):
            return Response(
                {"error": "Forbidden. Invalid API key."},
                status=status.HTTP_403_FORBIDDEN,
            )
        cart_key = request.data.get("cart_key")
        if not cart_key:
            return Response(
                {"error": "Cart key is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_data = redis_client.hgetall(cart_key)
        if not cart_data:
            return Response(
                {"error": "Cart not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_data = {
            key.decode("utf-8") if isinstance(key, bytes) else key: json.loads(
                value.decode("utf-8") if isinstance(value, bytes) else value
            )
            for key, value in cart_data.items()
        }

        total_price = Decimal(0)
        cart_details = []

        for product_id, product_data in cart_data.items():
            quantity = int(product_data["quantity"])
            price = Decimal(product_data["price"])
            discount = Decimal(product_data["discount"])
            price_after_discount = price * (1 - discount / 100)
            price_per_item = price_after_discount * quantity

            total_price += price_per_item

            cart_details.append(
                {
                    "product_id": product_id,
                    "name": product_data["name"],
                    "price": price,
                    "discount": discount,
                    "quantity": quantity,
                    "image": product_data["image"],
                    "price_after_discount": price_after_discount,
                    "price_per_item": price_per_item,
                }
            )

        total_price = str(total_price)

        return Response(
            {
                "cart_details": cart_details,
                "total_price": total_price,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["delete"])
    def clear_user_cart(self, request):
        permission = MicroservicePermission()
        if not permission.has_permission(request, self):
            return Response(
                {"error": "Forbidden. Invalid API key."},
                status=status.HTTP_403_FORBIDDEN,
            )
        cart_key = request.data.get("cart_key")
        if not cart_key:
            return Response(
                {"error": "Cart key is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        redis_client.delete(cart_key)

        return Response(
            {"message": f"Cart {cart_key} cleared"},
            status=status.HTTP_200_OK,
        )
