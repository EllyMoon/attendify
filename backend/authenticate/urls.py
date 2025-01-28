from django.urls import path
from .views import UserRegistrationView, UserLoginView, EmailVerificationView, PasswordResetView, PasswordResetConfirmView

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
     path('auth/verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('auth/reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('auth/reset-password/confirm/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
]