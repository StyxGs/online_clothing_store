from django.db import models

from products.models import Basket, Sizes
from users.models import User


class Order(models.Model):
    CREATED = 0
    PAID = 1
    ON_WAY = 2
    DELIVERED = 3
    STATUS = (
        (CREATED, 'Создан'),
        (PAID, 'Оплачен'),
        (ON_WAY, 'В пути'),
        (DELIVERED, 'Доставлен'),
    )

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=64)
    address = models.CharField(max_length=256)
    basket_history = models.JSONField(default=dict)
    time_created = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=CREATED, choices=STATUS)
    customer = models.ForeignKey(to=User, on_delete=models.PROTECT)

    def __str__(self):
        return f'Номер заказа: {self.id} | Заказ для {self.first_name}, {self.last_name}'

    def update_after_payment(self):
        baskets = Basket.objects.filter(user=self.customer)
        self.status = self.PAID
        self.basket_history = {
            'purchased_items': [basket.de_json() for basket in baskets],
            'total_sum': baskets.general_sum(),
        }
        baskets.delete()
        self.save()

    def update_quantity_sizes(self):
        update_size = self.basket_history['purchased_items']
        for goods in update_size:
            size = Sizes.objects.get(product__name=goods['product'])
            setattr(size, goods['size'], getattr(size, goods['size'])-int(goods['quantity']))
            size.save()
