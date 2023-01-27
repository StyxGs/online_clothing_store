from django.contrib import admin

from products.models import Basket, Categories, Products, Sizes

admin.site.register(Categories)


class SizeAdmin(admin.TabularInline):
    model = Sizes
    fields = ('XS', 'S', 'L', 'M', 'XL', 'XXL',)
    extra = 0


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'get_category')
    search_fields = ('name',)
    ordering = ('price',)
    inlines = (SizeAdmin,)


class BasketAdmin(admin.TabularInline):
    model = Basket
    fields = ('product', 'quantity', 'size')
    readonly_fields = ('created_timestamp',)
    extra = 0
