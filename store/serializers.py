from rest_framework import serializers
from decimal import Decimal

from store.models import Category


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)


class ProductSerializer(serializers.Serializer):
    TAX = 0.09

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    inventory = serializers.IntegerField()
    price_after_tax = serializers.SerializerMethodField()
    category = serializers.HyperlinkedRelatedField(
        queryset=Category.objects.all(),
        view_name="category_detail",
    )

    def get_price_after_tax(self, product):
        return round(product.unit_price * Decimal(1 + self.TAX), 2)