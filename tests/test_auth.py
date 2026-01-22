import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User'
    )


@pytest.mark.django_db
class TestAuthentication:
    
    def test_user_registration(self, api_client):
        """Test user registration endpoint"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123!',
            'password2': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '1234567890'
        }
        response = api_client.post('/api/auth/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert User.objects.filter(username='newuser').exists()
    
    def test_user_login(self, api_client, test_user):
        """Test user login endpoint"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self, api_client, test_user):
        """Test login with wrong password"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = api_client.post('/api/auth/login/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_without_auth(self, api_client):
        """Test accessing protected endpoint without token"""
        response = api_client.get('/api/auth/profile/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_auth(self, api_client, test_user):
        """Test accessing protected endpoint with valid token"""
        # Login first
        login_response = api_client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        token = login_response.data['access']
        
        # Access protected endpoint
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get('/api/auth/profile/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'