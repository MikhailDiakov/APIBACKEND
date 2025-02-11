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


PRODUCT_SERVICE = "http://127.0.0.1:8000/api/v1/product/"

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True
)


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
        # Получаем данные корзины
        cart_data = redis_client.hgetall(self.cart_key)

        # Декодируем данные, если они в байтах
        cart_data = {
            key.decode("utf-8") if isinstance(key, bytes) else key: json.loads(
                value.decode("utf-8") if isinstance(value, bytes) else value
            )
            for key, value in cart_data.items()
        }

        # Инициализация общей суммы
        total_price = Decimal(0)
        cart_details = []

        # Собираем данные о товарах и считаем общую стоимость
        for product_id, product_data in cart_data.items():
            # Извлекаем информацию о товаре
            quantity = int(product_data["quantity"])
            price = Decimal(product_data["price"])
            price_per_item = price * quantity

            # Обновляем общую цену
            total_price += price_per_item

            # Формируем данные для ответа
            cart_details.append(
                {
                    "product_id": product_id,
                    "name": product_data["name"],
                    "price": price,
                    "quantity": quantity,
                    "image": product_data["image"],
                    "price_per_item": price_per_item,
                }
            )

        # Преобразуем в строку для безопасности и точности
        total_price = str(total_price)

        return Response(
            {
                "cart_details": cart_details,
                "total_price": total_price,  # Включаем точную общую цену
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

        existing_item = redis_client.hget(self.cart_key, product_id)
        if existing_item:
            existing_item = json.loads(existing_item)
            existing_item["quantity"] += quantity
            redis_client.hset(self.cart_key, product_id, json.dumps(existing_item))
        else:
            cart_item = {
                "quantity": quantity,
                "name": product_info["name"],
                "price": product_info["price"],
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
