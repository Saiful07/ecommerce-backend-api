from django.urls import path
from .views import CartViewSet

urlpatterns = [
    path('cart/', CartViewSet.as_view({'get': 'view'}), name='cart-view'),
    path('cart/add/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add'),
    path('cart/items/<int:item_id>/', CartViewSet.as_view({
        'patch': 'update_item',
        'delete': 'remove_item'
    }), name='cart-item'),
    path('cart/clear/', CartViewSet.as_view({'delete': 'clear'}), name='cart-clear'),
]