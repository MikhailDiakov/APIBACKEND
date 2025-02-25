from django.contrib import admin
from django.urls import path, include
from main.views import ProductAPIview, CategoryViewSet
from rest_framework import routers
from main.schema import schema
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

router = routers.DefaultRouter()
router.register(r"product", ProductAPIview)
router.register(r"category", CategoryViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("", include("django_prometheus.urls")),
    path(
        "api/v1/graphql/",
        csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema)),
    ),
]
