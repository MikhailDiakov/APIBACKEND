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

USER_SERVICE_URL = settings.USER_SERVICE_URL


class ProductAPIview(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ["name"]

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

    def create(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user:
            return super().create(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def update(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user:
            return super().update(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def destroy(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user:
            return super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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

    def create(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user:
            return super().create(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def update(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user:
            return super().update(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def destroy(self, request, *args, **kwargs):
        user = self.get_user(request)
        if user:
            return super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

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
