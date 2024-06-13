from rest_framework import serializers
from decimal import Decimal
from django.utils.text import slugify

from store.models import Category, Product


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)


class ProductSerializer(serializers.ModelSerializer):
    TAX = 0.09

    title = serializers.CharField(max_length=255, source='name')
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source="unit_price")
    price_after_tax = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'category', 'price_after_tax', 'inventory', 'slug', 'description']
    

    def get_price_after_tax(self, product):
        return round(product.unit_price * Decimal(1 + self.TAX), 2)
    
    def validate(self, data):
        if len(data['name']) < 6:
            raise serializers.ValidationError("Product title should be at least 6.")
        return super().validate(data)
    
    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product