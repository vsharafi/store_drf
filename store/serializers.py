from rest_framework import serializers
from decimal import Decimal
from django.utils.text import slugify

from store.models import Cart, CartItem, Category, Comment, Product


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
        fields = ['id', 'name', 'body']

    def create(self, validated_data):
        product_pk = self.context['product_pk']
        return Comment.objects.create(product_id=product_pk, **validated_data)


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price', ]

class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        product = validated_data.get('product')
        quantity = validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product=product)
            cart_item.quantity += quantity
            cart_item.save()
        except cart_item.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)
        self.instance = cart_item
        return cart_item

class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)
    item_total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_total']
    
    def get_item_total(self, item:CartItem):
        return item.quantity * item.product.unit_price

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        read_only_fields = ['id']

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([(item.quantity*item.product.unit_price) for item in cart.items.all()])
