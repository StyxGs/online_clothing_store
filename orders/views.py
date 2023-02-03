import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from command.views import CommandContextMixin
from orders.forms import OrdersCreateForms
from orders.models import Order, User
from products.models import Basket

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(CommandContextMixin, TemplateView):
    template_name = 'orders/success.html'
    title = 'Store - Спасибо за заказ!'


class CancelView(TemplateView):
    template_name = 'orders/cancel.html'


class OrdersView(CommandContextMixin, ListView):
    template_name = 'orders/orders.html'
    title = 'Store - Заказы'
    queryset = Order.objects.all()
    context_object_name = 'orders'
    ordering = ('-time_created')

    def get_queryset(self):
        queryset = super(OrdersView, self).get_queryset()
        return queryset.filter(customer=self.request.user)


class LookOrderView(DetailView):
    template_name = 'orders/order.html'
    model = Order
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super(LookOrderView, self).get_context_data(**kwargs)
        context['title'] = f'Store - Заказ #{self.object.id}'
        return context


class CreateOrdersView(CommandContextMixin, CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrdersCreateForms
    success_url = reverse_lazy('orders:orders_success')
    title = 'Store - оформление заказа'

    def post(self, request, *args, **kwargs):
        baskets = Basket.objects.filter(user=self.request.user)
        checkout_session = stripe.checkout.Session.create(
            line_items=baskets.stripe_price(),
            metadata={'first_name': request.POST['first_name'],
                      'last_name': request.POST['last_name'],
                      'email': request.POST['email'],
                      'address': request.POST['address'],
                      'id': request.user.id},
            mode='payment',
            success_url='{}{}'.format(settings.DOMAIN_NAME, reverse_lazy('orders:orders_success')),
            cancel_url='{}{}'.format(settings.DOMAIN_NAME, reverse_lazy('orders:orders_cancel')),
        )
        return HttpResponseRedirect(checkout_session.url, status=303)

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super(CreateOrdersView, self).form_valid(form)


@csrf_exempt
def store_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )
        line_items = session
        # Fulfill the purchase...
        fulfill_order(line_items)

    # Passed signature verification
    return HttpResponse(status=200)


def fulfill_order(line_items):
    order = Order.objects.create(first_name=line_items.metadata.first_name,
                                 last_name=line_items.metadata.last_name,
                                 email=line_items.metadata.email,
                                 address=line_items.metadata.address,
                                 customer=User.objects.get(id=line_items.metadata.id)
                                 )
    order.update_after_payment()
    order.update_quantity_sizes()

