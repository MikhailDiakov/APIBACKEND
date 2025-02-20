from django.contrib import admin
from django.urls import path, include
from main.views import ProductAPIview, CategoryViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"product", ProductAPIview)
router.register(r"category", CategoryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("", include("django_prometheus.urls")),
]
