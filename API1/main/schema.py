import graphene
from graphene_django.types import DjangoObjectType
from .models import Product, Category


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class Query(graphene.ObjectType):
    all_products = graphene.List(ProductType)
    all_categories = graphene.List(CategoryType)
    product = graphene.Field(ProductType, id=graphene.Int())
    category = graphene.Field(CategoryType, id=graphene.Int())

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_categories(self, info):
        return Category.objects.all()

    def resolve_product(self, info, id):
        return Product.objects.get(id=id)

    def resolve_category(self, info, id):
        return Category.objects.get(id=id)


schema = graphene.Schema(query=Query)
