from datetime import timedelta
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from products.models import Basket, Products
from users.models import EmailVerification, User


class UserViewTestCase(TestCase):
    fixtures = ['categories.json', 'goods.json']

    def setUp(self):
        self.path = reverse('users:registrations')
        self.data = {
            'first_name': 'Georgia', 'last_name': 'Sychev',
            'username': 'gosha', 'email': 'gosha@mail.ru',
            'password1': 'gosha191101', 'password2': 'gosha191101',
        }
        self.username = self.data['username']

    def _check_login(self):
        # creating of user
        self.client.post(self.path, self.data)
        # check login
        login = self.client.post(reverse('users:login'), {'username': self.username,
                                                          'password': self.data['password1']})
        self.assertEqual(login.status_code, HTTPStatus.FOUND)
        self.assertRedirects(login, reverse('users:email_activation'))

    def test_user_registration_get(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/registrations.html')

    def test_user_registration_post_success(self):
        response = self.client.post(self.path, self.data)

        # Check creating of user
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(username=self.username).exists())

        # Check creating of Email Verification
        email_verification = EmailVerification.objects.filter(user__username=self.username)
        self.assertTrue(email_verification.exists())
        self.assertEqual(email_verification.first().expirations.date(),
                         (now() + timedelta(hours=48)).date())

    def test_login_and_basket(self):
        # Check log in account
        self._check_login()
        # activate the email to be able to add the product to the card
        user = User.objects.first()
        user.is_verified_email = True
        user.save()

        # Check add to the product to the basket
        product = Products.objects.first()
        path = reverse('products:basket_add', kwargs={'product_id': product.id})
        basket_add = self.client.get(path)
        basket = Basket.objects.filter(user=user)
        self.assertEqual(basket_add.status_code, HTTPStatus.FOUND)
        self.assertTrue(basket.exists())

        # Check remove a product from the basket
        path = reverse('products:basket_remove', kwargs={'basket_id': basket.first().product.id})
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_logout(self):
        # login
        self._check_login()
        # logout
        path = reverse('users:logout')
        response = self.client.post(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('index'))


