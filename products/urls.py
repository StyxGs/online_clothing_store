from django.urls import path

from products.views import (ProductDetailView, ProductsListView, basket_add,
                            basket_remove)

app_name = 'products'

urlpatterns = [
    path('', ProductsListView.as_view(), name='index'),
    path('category/<int:category_id>/', ProductsListView.as_view(), name='category'),
    path('basket/<int:product_id>/', basket_add, name='basket_add'),
    path('basket/remove/<int:basket_id>/', basket_remove, name='basket_remove'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='detail_product'),
]
