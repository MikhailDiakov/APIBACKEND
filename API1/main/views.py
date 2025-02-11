from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, Category
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter


class ProductAPIview(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProductFilter
    search_fields = ["name"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(methods=["get"], detail=True)
    def products(self, request, pk=None):
        category = Category.objects.get(pk=pk)
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
