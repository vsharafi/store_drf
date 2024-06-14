from django.urls import path
from store import views


urlpatterns = [
    path('products/', views.product_list),
    path('products/<int:pk>/', views.product_detail),
    path('categories/', views.category_list),
    path('categories/<int:pk>/', views.category_detail, name="category_detail")
]
