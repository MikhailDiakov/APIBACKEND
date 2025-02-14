from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from django.conf import settings
import requests
from decimal import Decimal
from rest_framework.permissions import BasePermission

CART_SERVICE_URL = "http://127.0.0.1:8001/api/v1/cart/"
USER_SERVICE_URL = "http://127.0.0.1:8003/api/v1/users/"


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
        is_admin = False

        if not is_microservice:
            user = self.get_user(request)
            if user:
                is_admin = True

        if not is_microservice and not is_admin:
            return Response(
                {"error": "Forbidden. Access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        order_id = request.data.get("order_id")
        status_value = request.data.get("status")
        is_paid = request.data.get("is_paid")

        if not order_id:
            return Response(
                {"error": "Order ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if status_value:
            if status_value not in [Order.PENDING, Order.COMPLETED, Order.CANCELLED]:
                return Response(
                    {"error": "Invalid status value."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            order.status = status_value
        if is_microservice and is_paid is not None:
            order.is_paid = is_paid

        order.save()

        return Response(
            {"message": "Order updated successfully."}, status=status.HTTP_200_OK
        )

    def get_user(self, request):
        token = request.headers.get("Authorization")
        if not token:
            return None

        headers = {"Authorization": token}
        response = requests.get(
            f"{USER_SERVICE_URL}check-admin-status/", headers=headers
        )

        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("is_admin"):
                return user_data
        return None

    @action(detail=False, methods=["get"])
    def get_orders(self, request):
        token = request.headers.get("Authorization", "").replace("Token ", "")

        if token:
            user_info = self.get_user_info(token)
            if user_info:
                user_id = user_info.get("id")
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
                {"error": "No orders found for this cart key."},
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
                "phone": order.phone,
                "email": order.email,
            }
            for order in orders
        ]

        return Response(
            {"orders": order_data},
            status=status.HTTP_200_OK,
        )

    def get_user_info(self, token):
        url = f"{USER_SERVICE_URL}me/"
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return response.json()
        return None
