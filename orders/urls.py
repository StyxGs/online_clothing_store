from django.urls import path

from orders.views import (CancelView, CreateOrdersView, LookOrderView,
                          OrdersView, SuccessView)

app_name = 'orders'

urlpatterns = [
    path('order_create/', CreateOrdersView.as_view(), name='orders_create'),
    path('success/', SuccessView.as_view(), name='orders_success'),
    path('cancel/', CancelView.as_view(), name='orders_cancel'),
    path('orders/', OrdersView.as_view(), name='orders_list'),
    path('order/<int:pk>/', LookOrderView.as_view(), name='look_order'),
]
