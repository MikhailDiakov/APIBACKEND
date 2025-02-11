from django_filters import rest_framework as filters
from django.db.models import F, ExpressionWrapper, DecimalField
from .models import Product


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains", label="Search by name")
    price_min = filters.NumberFilter(method="filter_price_min", label="Min sell price")
    price_max = filters.NumberFilter(method="filter_price_max", label="Max sell price")
    discount_min = filters.NumberFilter(
        field_name="discount", lookup_expr="gte", label="Min discount"
    )
    discount_max = filters.NumberFilter(
        field_name="discount", lookup_expr="lte", label="Max discount"
    )
    available = filters.BooleanFilter(field_name="available", label="Availability")

    class Meta:
        model = Product
        fields = [
            "name",
            "price_min",
            "price_max",
            "discount_min",
            "discount_max",
            "available",
        ]

    def annotate_sell_price(self, queryset):

        return queryset.annotate(
            sell_price=ExpressionWrapper(
                F("price") - (F("price") * F("discount") / 100),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )

    def filter_price_min(self, queryset, name, value):
        queryset = self.annotate_sell_price(queryset)
        return queryset.filter(sell_price__gte=value)

    def filter_price_max(self, queryset, name, value):
        queryset = self.annotate_sell_price(queryset)
        return queryset.filter(sell_price__lte=value)
