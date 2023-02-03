from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from products.models import Categories, Products


class IndexViewTestCase(TestCase):

    def test_index(self):
        path = reverse('index')
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.OK)


class ProductsViewTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.products = Products.objects.all()

    def _command_tests(self, response):
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'products/products.html')

    def test_list(self):
        path = reverse('products:index')
        response = self.client.get(path)

        self._command_tests(response)
        self.assertEqual(list(response.context_data['object_list']), list(self.products[:3]))

    def test_list_category(self):
        category = Categories.objects.first()
        path = reverse('products:category', kwargs={'category_id': category.id})
        response = self.client.get(path)

        self._command_tests(response)
        self.assertEqual(
            list(response.context_data['object_list']),
            list(self.products.filter(category=category.id))
        )

    def test_basket_add(self):
        basket = self.products.first()
        path = reverse('products:basket_add', kwargs={'product_id': basket.id})
        response = self.client.get(path)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)