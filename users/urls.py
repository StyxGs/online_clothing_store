from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import (EmailResending, EmailVerificationView,
                         RegistrationsView, UserLoginView, UserProfileView,
                         resending_an_email)

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('registrations/', RegistrationsView.as_view(), name='registrations'),
    path('profiles/<int:pk>/', login_required(UserProfileView.as_view()), name='profiles'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:email>/<uuid:code>/', EmailVerificationView.as_view(), name='verify'),
    path('email_activation/<int:pk>/', EmailResending.as_view(), name='email_activation'),
    path('resending_an_email/', resending_an_email, name='resending_an_email'),
]
