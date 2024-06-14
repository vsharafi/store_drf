from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Category, Product, Comment
from .serializers import CategorySerializer, CommentSerializer, ProductSerializer


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category_id', 'inventory']


    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, pk):
        product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
        if product.order_items.count() > 0:
            return Response({'error': "There is some order item including this product. Please remove them first."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset =  Category.objects.prefetch_related('products')

    def destroy(self, request, pk):
        category = get_object_or_404(Category.objects.annotate(products_count=Count('products')), pk=pk)
        if category.products.count() > 0:
            return Response({'error': "There is some product item in this category. Please remove them first."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        product_pk = self.kwargs['product_pk']
        return Comment.objects.filter(product_id=product_pk)
    
    def get_serializer_context(self):
        return {'product_pk': self.kwargs['product_pk']}