from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from command.views import CommandContextMixin
from products.models import Basket, Categories, Products, Sizes


class IndexView(CommandContextMixin, TemplateView):
    template_name = 'products/index.html'
    title = 'Store'


class ProductsListView(CommandContextMixin, ListView):
    template_name = 'products/products.html'
    queryset = Products.objects.all()
    context_object_name = "products"
    paginate_by = 3
    title = 'Store-каталог'

    def get_queryset(self):
        queryset = super(ProductsListView, self).get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category=category_id) if category_id else queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductsListView, self).get_context_data()
        context['categories'] = Categories.objects.all()
        products = cache.get('products')
        if not products:
            cache.set('products', context['products'], 60)
        return context


class ProductDetailView(SuccessMessageMixin, DetailView):
    model = Products
    template_name = 'products/product.html'
    context_object_name = "product"
    success_message = 'Товар добавлен в корзину'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data()
        context['title'] = f'Store - {self.object.name}'
        context['enable_size'] = Sizes.objects.filter(product_id=self.kwargs['pk']).values('XS', 'S', 'M', 'L', 'XL',
                                                                                           'XXL').first()
        return context

    def get(self, request, *args, **kwargs):
        context = super(ProductDetailView, self).get(request, *args, **kwargs)
        if self.request.GET:
            request.session['size'] = self.request.GET['size']
        return context


@login_required
def basket_add(request, product_id):
    if request.user.is_verified_email:
        size = request.session.get('size')
        Basket.update_or_create_basket(product_id, request.user, size)
        messages.success(request, 'Товар добавлен в корзину!')
        return HttpResponseRedirect(reverse('products:detail_product', args=(product_id,)))
    else:
        return HttpResponseRedirect(reverse('users:email_activation'))


def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
