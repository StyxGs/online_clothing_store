from django.contrib import admin

from products.admin import BasketAdmin
from users.models import EmailVerification, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    inlines = (BasketAdmin,)


@admin.register(EmailVerification)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'expirations')
    fields = ('email', 'user', 'expirations', 'created')
    readonly_fields = ('created',)

