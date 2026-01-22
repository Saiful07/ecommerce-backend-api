import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Category, Product
from carts.models import Cart, CartItem
from orders.models import Order

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def category(db):
    return Category.objects.create(name='Electronics')


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name='Test Product',
        category=category,
        price=100.00,
        stock=10
    )


@pytest.fixture
def cart_with_items(db, test_user, product):
    cart = Cart.objects.create(user=test_user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart


@pytest.mark.django_db
class TestOrders:
    
    def test_create_order_from_cart(self, authenticated_client, cart_with_items, product):
        """Test creating order from cart"""
        data = {
            'shipping_address': '123 Test St, City, State, 12345, Country'
        }
        response = authenticated_client.post('/api/orders/create_order/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'order_number' in response.data
        assert float(response.data['total_amount']) == 200.00
        
        # Check stock was deducted
        product.refresh_from_db()
        assert product.stock == 8
    
    def test_create_order_empty_cart(self, authenticated_client, test_user):
        """Test creating order with empty cart"""
        Cart.objects.create(user=test_user)
        
        data = {
            'shipping_address': '123 Test St, City, State, 12345, Country'
        }
        response = authenticated_client.post('/api/orders/create_order/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'empty' in response.data['error'].lower()
    
    def test_list_user_orders(self, authenticated_client, test_user):
        """Test listing user's orders"""
        Order.objects.create(
            user=test_user,
            total_amount=100.00,
            shipping_address='Test address'
        )
        
        response = authenticated_client.get('/api/orders/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_cancel_order(self, authenticated_client, test_user, product):
        """Test order cancellation"""
        order = Order.objects.create(
            user=test_user,
            total_amount=100.00,
            shipping_address='Test address',
            status='pending'
        )
        
        from orders.models import OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            price_at_purchase=100.00
        )
        
        # Deduct stock
        product.stock = 8
        product.save()
        
        response = authenticated_client.post(f'/api/orders/{order.id}/cancel/')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check stock was restored
        product.refresh_from_db()
        assert product.stock == 10