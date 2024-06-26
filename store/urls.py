from django.urls import path, include
from store import views
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('products', viewset=views.ProductViewSet, basename='product')
router.register('categories', viewset=views.CategoryViewSet, basename='category')
router.register('carts', viewset=views.CartViewSet, basename='cart')
router.register('customers', viewset=views.CustomerViewSet, basename='customer')
router.register('orders', viewset=views.OrderViewSet, basename='order')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register(r'comments', viewset=views.CommentViewSet, basename='product-comments')

Carts_router = routers.NestedDefaultRouter(router, 'carts', lookup="cart")
Carts_router.register(r'items', viewset=views.CartItemViewSet, basename='cart-items')


urlpatterns = router.urls + products_router.urls + Carts_router.urls

# urlpatterns = [
#     path('', include(router.urls))
# ]


# urlpatterns = [
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>/', views.ProductDetail.as_view()),
#     path('categories/', views.CategoryList.as_view()),
#     path('categories/<int:pk>/', views.CategoryDetail.as_view(), name="category_detail")
# ]
