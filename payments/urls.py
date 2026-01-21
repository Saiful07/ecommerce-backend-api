from django.urls import path
from .views import PaymentViewSet

urlpatterns = [
    path('payments/initiate/', PaymentViewSet.as_view({'post': 'initiate'}), name='payment-initiate'),
    path('payments/verify/', PaymentViewSet.as_view({'post': 'verify'}), name='payment-verify'),
    path('payments/webhook/', PaymentViewSet.as_view({'post': 'webhook'}), name='payment-webhook'),
]