import pytest
from rest_framework.test import APIClient
from rest_framework import status
from products.models import Category, Product
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='Admin123!'
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name='Electronics',
        description='Electronic items'
    )


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name='Test Product',
        category=category,
        price=99.99,
        stock=10,
        description='Test description'
    )


@pytest.mark.django_db
class TestProducts:
    
    def test_list_products(self, api_client, product):
        """Test listing products endpoint"""
        response = api_client.get('/api/products/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'Test Product'
    
    def test_product_detail(self, api_client, product):
        """Test product detail endpoint"""
        response = api_client.get(f'/api/products/{product.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Product'
        assert float(response.data['price']) == 99.99
    
    def test_search_products(self, api_client, product):
        """Test product search functionality"""
        response = api_client.get('/api/products/?search=Test')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_filter_by_category(self, api_client, product, category):
        """Test filtering products by category"""
        response = api_client.get(f'/api/products/?category={category.slug}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_create_product_without_auth(self, api_client, category):
        """Test creating product without authentication"""
        data = {
            'name': 'New Product',
            'category': category.id,
            'price': 49.99,
            'stock': 5
        }
        response = api_client.post('/api/products/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_product_as_admin(self, api_client, admin_user, category):
        """Test creating product as admin"""
        api_client.force_authenticate(user=admin_user)
        
        data = {
            'name': 'New Product',
            'category': category.id,
            'price': 49.99,
            'stock': 5,
            'description': 'New product description'
        }
        response = api_client.post('/api/products/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(name='New Product').exists()