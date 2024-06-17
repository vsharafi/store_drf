from rest_framework import serializers
from decimal import Decimal
from django.utils.text import slugify
from django.db import transaction

from store.models import Cart, CartItem, Category, Comment, Customer, Order, OrderItem, Product


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


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        product = validated_data.get('product')
        quantity = validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user', 'birth_date']
        read_only_fields = ['user', ]



class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price', ]

class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, source='user.first_name')
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'birth_date']



class OrderForAdminSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = OrderCustomerSerializer()
    class Meta:
        model = Order
        fields = ['id', 'items', 'customer', 'status', 'datetime_created']
        read_only_fields = ['customer', 'status']


class OrderForUserSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'items', 'status', 'datetime_created']
        read_only_fields = ['customer', 'status']


class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('There is no cart with this cart id!')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Your cart is empty! Please add some product to it first.')
        return cart_id
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id=user_id)

            order = Order()
            order.customer = customer
            order.save()
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = [
                            OrderItem(
                                    order = order,
                                    product_id = item.product_id,
                                    unit_price = item.product.unit_price,
                                    quantity = item.quantity
                                ) for item in cart_items
                        ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.get(id=cart_id).delete()
            return order