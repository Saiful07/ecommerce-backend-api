from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView
from django.contrib.auth import get_user_model
from django.db import transaction
from .serializers import UserRegistrationSerializer, UserSerializer, ChangePasswordSerializer

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Merge anonymous cart if exists
        self.merge_session_cart(request, user)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    
    def merge_session_cart(self, request, user):
        """Merge session cart into user cart on registration"""
        from carts.models import Cart, CartItem
        
        session_key = request.session.session_key
        if not session_key:
            return
        
        try:
            session_cart = Cart.objects.get(session_key=session_key, user=None)
        except Cart.DoesNotExist:
            return
        
        # Get or create user cart
        user_cart, created = Cart.objects.get_or_create(user=user, session_key=None)
        
        with transaction.atomic():
            for session_item in session_cart.items.all():
                user_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=session_item.product,
                    defaults={'quantity': session_item.quantity}
                )
                
                if not created:
                    # Item exists, add quantities
                    user_item.quantity += session_item.quantity
                    user_item.save()
            
            # Delete session cart
            session_cart.delete()


class TokenObtainPairView(BaseTokenObtainPairView):
    """Custom login view with cart migration"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user from token
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = response.data.get('access')
            token = AccessToken(access_token)
            user_id = token['user_id']
            
            user = User.objects.get(id=user_id)
            self.merge_session_cart(request, user)
        
        return response
    
    def merge_session_cart(self, request, user):
        """Merge session cart into user cart on login"""
        from carts.models import Cart, CartItem
        
        session_key = request.session.session_key
        if not session_key:
            return
        
        try:
            session_cart = Cart.objects.get(session_key=session_key, user=None)
        except Cart.DoesNotExist:
            return
        
        # Get or create user cart
        user_cart, created = Cart.objects.get_or_create(user=user, session_key=None)
        
        with transaction.atomic():
            for session_item in session_cart.items.all():
                user_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=session_item.product,
                    defaults={'quantity': session_item.quantity}
                )
                
                if not created:
                    # Item exists, add quantities
                    user_item.quantity += session_item.quantity
                    user_item.save()
            
            # Delete session cart
            session_cart.delete()


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)