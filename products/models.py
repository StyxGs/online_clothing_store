import stripe
from django.conf import settings
from django.db import models

from users.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY


class Categories(models.Model):
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Products(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='products_images')
    description = models.TextField()
    price = models.IntegerField()
    quantity = models.PositiveIntegerField(default=0)
    stripe_product_id = models.CharField(max_length=128, null=True, blank=True)
    category = models.ManyToManyField(Categories)

    def __str__(self):
        return f'Продукт: {self.name}'

    def get_category(self):
        return ", ".join([categories.name for categories in self.category.all()])

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.stripe_product_id:
            stripe_product_price = self.create_stripe_product_price()
            self.stripe_product_id = stripe_product_price['id']
        super(Products, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

    def create_stripe_product_price(self):
        stripe_product = stripe.Product.create(name=self.name)
        stripe_product_price = stripe.Price.create(
            product=stripe_product['id'],
            unit_amount=round(self.price * 100),
            currency='rub'
        )
        return stripe_product_price


class Sizes(models.Model):
    product = models.ForeignKey(to=Products, on_delete=models.CASCADE, null=True, blank=True)
    XS = models.PositiveSmallIntegerField(default=0)
    S = models.PositiveSmallIntegerField(default=0)
    M = models.PositiveSmallIntegerField(default=0)
    L = models.PositiveSmallIntegerField(default=0)
    XL = models.PositiveSmallIntegerField(default=0)
    XXL = models.PositiveSmallIntegerField(default=0)


class BasketQuerySet(models.QuerySet):

    def general_quantity(self):
        return sum(basket.quantity for basket in self)

    def general_sum(self):
        return sum(basket.sum() for basket in self)

    def stripe_price(self):
        line_items = []
        for basket in self:
            item = {
                'price': basket.product.stripe_product_id,
                'quantity': basket.quantity,
            }
            line_items.append(item)
        return line_items


class Basket(models.Model):
    SIZES = ((0, 'XS'),
             (1, 'S'),
             (2, 'M'),
             (3, 'L'),
             (4, 'XL'),
             (5, 'XXL'))

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(to=Products, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)
    size = models.SmallIntegerField(default=0, choices=SIZES)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    objects = BasketQuerySet.as_manager()

    def sum(self):
        return self.product.price * self.quantity

    def de_json(self):
        basket_items = {
            'product': self.product.name,
            'quantity': self.quantity,
            'price': self.product.price,
            'size': self.get_size_display(),
            'sum': self.sum()
        }
        return basket_items

    @classmethod
    def update_or_create_basket(cls, product_id, user, size):
        sizes = {'XS': 0, 'S': 1, 'M': 2, 'L': 3, 'XL': 4, 'XXL': 5}
        baskets = Basket.objects.filter(user=user, product_id=product_id, size=sizes[size])
        if not baskets.exists():
            obj = Basket.objects.create(user=user, product_id=product_id, quantity=1, size=sizes[size])
            is_created = True
            return obj, is_created
        else:
            basket = baskets.first()
            basket.quantity += 1
            basket.save()
            is_created = False
            return basket, is_created
