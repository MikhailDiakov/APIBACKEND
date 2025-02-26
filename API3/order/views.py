from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from django.conf import settings
import requests
from decimal import Decimal
from rest_framework.permissions import BasePermission
from .tasks import update_order_task
import re
from .logs_service import log_to_kafka
import jwt
from rest_framework_simplejwt.authentication import JWTAuthentication

CART_SERVICE_URL = settings.CART_SERVICE_URL


class MicroservicePermission(BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get("X-MICROSERVICE-API-KEY")
        return api_key == settings.MICROSERVICE_API_KEY


class OrderViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"])
    def create_order(self, request):
        cart_key = request.data.get("cart_key")
        if not cart_key:
            return Response(
                {"error": "Cart key is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shipping_address = request.data.get("shipping_address")
        city = request.data.get("city")
        postcode = request.data.get("postcode")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        phone_number = request.data.get("phone_number", "")
        email = request.data.get("email", "")
        notes = request.data.get("notes", "")

        cart_url = f"{CART_SERVICE_URL}get_user_cart/"
        headers = {
            "X-MICROSERVICE-API-KEY": settings.MICROSERVICE_API_KEY,
        }
        response = requests.get(
            cart_url,
            headers=headers,
            json={"cart_key": cart_key},
        )

        if response.status_code != 200:
            return Response(
                {"error": "Failed to fetch cart data."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        cart_data = response.json()
        cart_details = cart_data.get("cart_details", {})
        total_price = Decimal(cart_data.get("total_price", 0))

        order = Order.objects.create(
            cart_key=cart_key,
            total_price=total_price,
            status=Order.PENDING,
            shipping_address=shipping_address,
            city=city,
            postcode=postcode,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            notes=notes,
            is_paid=False,
        )

        for product_data in cart_details:
            product_id = product_data["product_id"]
            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                name=product_data["name"],
                quantity=product_data["quantity"],
                price=Decimal(product_data["price"]),
                discount=Decimal(product_data["discount"]),
                price_after_discount=Decimal(product_data["price_after_discount"]),
                price_per_item=Decimal(product_data["price_per_item"]),
                image=product_data["image"],
            )

        clear_cart_url = f"{CART_SERVICE_URL}clear_user_cart/"
        response_clear = requests.delete(
            clear_cart_url,
            headers=headers,
            json={"cart_key": cart_key},
        )

        if response_clear.status_code != 200:
            order.delete()
            return Response(
                {"error": "Failed to clear the cart after order creation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        log_to_kafka(
            message="Order Created",
            level="info",
            extra_data={
                "event": "order_created",
                "order_id": order.id,
                "cart_key": cart_key,
                "status": "success",
            },
        )
        return Response(
            {
                "message": "Order created successfully",
                "order_id": order.id,
                "cart_key": cart_key,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["put"])
    def update_order(self, request):
        permission = MicroservicePermission()
        is_microservice = permission.has_permission(request, self)
        is_admin = self.is_admin_user(request)

        if not is_microservice and not is_admin:
            return Response(
                {"error": "Forbidden. Access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order_id = request.data.get("order_id")
        status_value = request.data.get("status")
        is_paid = request.data.get("is_paid")
        payment_intent = request.data.get("payment_intent")

        if not order_id:
            return Response(
                {"error": "Order ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if status_value not in dict(Order.ORDER_STATUS_CHOICES):
            return Response(
                {"error": "Invalid status value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        update_order_task.delay(
            order_id=order_id,
            status_value=status_value,
            is_paid=is_paid if is_microservice else None,
            payment_intent=payment_intent,
        )

        return Response(
            {"message": "Order updated successfully."}, status=status.HTTP_200_OK
        )

    def is_admin_user(self, request):
        auth = JWTAuthentication()
        token = request.headers.get("Authorization")
        if not token:
            return False
        try:
            validated_token = auth.get_validated_token(token.split()[1])
            return validated_token.get("is_admin", False)
        except Exception:
            return False

    @action(detail=False, methods=["get"])
    def get_orders(self, request):
        token = request.headers.get("Authorization")
        if token:
            user_info = self.get_user_info_from_token(token)
            if user_info:
                user_id = user_info.get("user_id")
                cart_key = f"cart_{user_id}"
            else:
                return Response(
                    {"error": "Invalid token."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        orders = Order.objects.filter(cart_key=cart_key)

        if not orders:
            return Response(
                {"error": "No orders found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        order_data = [
            {
                "order_id": order.id,
                "total_price": str(order.total_price),
                "status": order.status,
                "is_paid": order.is_paid,
                "shipping_address": order.shipping_address,
                "first_name": order.first_name,
                "last_name": order.last_name,
                "phone_number": order.phone_number,
                "email": order.email,
            }
            for order in orders
        ]

        return Response(
            {"orders": order_data},
            status=status.HTTP_200_OK,
        )

    def get_user_info_from_token(self, token):
        auth = JWTAuthentication()

        try:
            validated_token = auth.get_validated_token(token.split()[1])
            return validated_token
        except Exception:
            return None

    @action(detail=True, methods=["post"])
    def get_order_by_id(self, request, pk=None):
        permission = MicroservicePermission()
        is_microservice = permission.has_permission(request, self)

        if not is_microservice:
            return Response(
                {"error": "Forbidden. Access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = request.headers.get("Authorization")
        user_info = self.get_user_info_from_token(token) if token else None

        if user_info:
            user_id = user_info.get("user_id")
            if order.cart_key != f"cart_{user_id}":
                return Response(
                    {"error": "Forbidden. This order does not belong to you."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            cart_key = request.data.get("cart_key")
            if (
                not cart_key
                or order.cart_key != cart_key
                or is_sequential_cart_key(cart_key)
            ):
                return Response(
                    {"error": "Forbidden. Invalid cart key."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        items_data = [
            {
                "product_name": item.name,
                "quantity": item.quantity,
                "unit_price": str(item.price_after_discount),
            }
            for item in order.items.all()
        ]

        order_data = {
            "order_id": order.id,
            "total_price": str(order.total_price),
            "items": items_data,
        }

        return Response(
            {"order": order_data},
            status=status.HTTP_200_OK,
        )


def is_sequential_cart_key(cart_key):
    if re.match(r"^cart_\d+$", cart_key):
        number_part = cart_key.split("_")[1]
        return number_part.isdigit() and int(number_part) == int(number_part)
    return False
