from rest_framework import serializers
from decimal import Decimal
from django.utils.text import slugify

from store.models import Category, Comment, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'product_number']
    # product_number = serializers.SerializerMethodField(read_only=True)
    product_number = serializers.IntegerField(read_only=True, source='products.count')

    # def get_product_number(self, category):
    #     try:
    #         num = category.product_count
    #     except AttributeError:
    #         num = 0
    #     return num
    
    def validate(self, data):
        if len(data['title']) < 3:
            raise serializers.ValidationError("Category title should be at least 6.")
        return super().validate(data)

class ProductSerializer(serializers.ModelSerializer):
    TAX = 0.09

    title = serializers.CharField(max_length=255, source='name')
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source="unit_price")
    price_after_tax = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'category', 'price_after_tax', 'inventory', 'description']
    

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
    
    # def update(self, instance, validated_data):
    #     instance.inventory = validated_data.get('inventory')
    #     instance.save()
    #     return instance



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'product', 'name', 'body']