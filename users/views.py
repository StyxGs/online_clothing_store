from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from command.views import CommandContextMixin
from users.forms import UserLoginForm, UserProfilesForm, UserRegistrationsForm
from users.models import EmailVerification, User
from users.tasks import send_email_create


class UserLoginView(CommandContextMixin, LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('index')
    title = 'Store - Вход'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        if form.user_cache.is_verified_email:
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseRedirect(reverse('users:email_activation'))


class RegistrationsView(CommandContextMixin, SuccessMessageMixin, CreateView):
    model = User
    template_name = 'users/registrations.html'
    form_class = UserRegistrationsForm
    success_url = reverse_lazy('users:login')
    success_message = 'Письмо для подтверждения электронной почты отправлено!'
    title = 'Store - регистрация'


class UserProfileView(SuccessMessageMixin, CommandContextMixin, UpdateView):
    model = User
    template_name = 'users/profiles.html'
    form_class = UserProfilesForm
    success_message = 'Изменения сохранены!'
    title = 'Store - Личный кабинет'

    def get(self, request, *args, **kwargs):
        current_user = User.objects.get(id=self.request.user.pk)
        if current_user.pk != kwargs['pk']:
            return HttpResponseRedirect(reverse('users:profiles', args=(self.request.user.pk,)))
        else:
            return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('users:profiles', args=(self.object.id,))


class EmailVerificationView(CommandContextMixin, TemplateView):
    title = 'Store - подтверждение электронной почты'
    template_name = 'users/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        email_verification = EmailVerification.objects.filter(user=user, code=code)
        if email_verification.exists() and email_verification.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('index'))


class EmailResending(CommandContextMixin, TemplateView):
    title = 'Store - активация электронной почты'
    template_name = 'users/email_activate.html'


def resending_an_email(request):
    user = User.objects.get(username=request.user)
    email = EmailVerification.objects.get(user=user)
    email.delete()
    send_email_create.delay(user.id)
    return HttpResponseRedirect(reverse('index'))
