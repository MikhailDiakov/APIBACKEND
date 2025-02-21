from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, Category
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
import requests
from django.conf import settings
from .filters import ProductFilter
from .logs_service import log_to_kafka
from rest_framework_simplejwt.authentication import JWTAuthentication

USER_SERVICE_URL = settings.USER_SERVICE_URL


class AdminRequiredMixin:

    def get_user_from_token(self, request):
        auth = JWTAuthentication()
        token = request.headers.get("Authorization")
        if not token:
            return None

        try:
            validated_token = auth.get_validated_token(token.split()[1])
            return validated_token.get("is_admin", False)
        except Exception:
            return None

    def is_admin(self, request):
        return self.get_user_from_token(request)


class ProductAPIview(AdminRequiredMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ["name"]

    def create(self, request, *args, **kwargs):
        if not self.is_admin(request):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        log_to_kafka(
            message="Admin created a new product.",
            level="info",
            extra_data={"action": "create", "product_data": request.data},
        )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not self.is_admin(request):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        log_to_kafka(
            message="Admin updated a product.",
            level="info",
            extra_data={
                "action": "update",
                "product_id": kwargs["pk"],
                "updated_data": request.data,
            },
        )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self.is_admin(request):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        log_to_kafka(
            message="Admin deleted a product.",
            level="info",
            extra_data={"action": "delete", "product_id": kwargs["pk"]},
        )
        return super().destroy(request, *args, **kwargs)


class CategoryViewSet(AdminRequiredMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        if not self.is_admin(request):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        log_to_kafka(
            message="Admin created a new category.",
            level="info",
            extra_data={"action": "create", "category_data": request.data},
        )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not self.is_admin(request):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        log_to_kafka(
            message="Admin updated a category.",
            level="info",
            extra_data={
                "action": "update",
                "category_id": kwargs["pk"],
                "updated_data": request.data,
            },
        )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self.is_admin(request):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        log_to_kafka(
            message="Admin deleted a category.",
            level="info",
            extra_data={"action": "delete", "category_id": kwargs["pk"]},
        )
        return super().destroy(request, *args, **kwargs)

    @action(methods=["get"], detail=True)
    def products(self, request, pk=None):
        category = Category.objects.get(pk=pk)
        products = Product.objects.filter(category=category)

        filterset = ProductFilter(request.GET, queryset=products)
        if filterset.is_valid():
            products = filterset.qs

        search_query = request.GET.get("search", None)
        if search_query:
            products = products.filter(name__icontains=search_query)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
