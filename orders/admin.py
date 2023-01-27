from django.contrib import admin

from orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')
    fields = (
        'id',
        'first_name', 'last_name',
        'email', 'address',
        'time_created',
        'customer',
        'basket_history',
        'status')
    readonly_fields = ('id', 'time_created',)
