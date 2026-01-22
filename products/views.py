from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django.db.models import Q, Sum, Count, F
from .models import Category, Product
from .serializers import (
    CategorySerializer, 
    ProductListSerializer, 
    ProductDetailSerializer,
    ProductCreateUpdateSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        """Get all categories including nested ones"""
        categories = Category.objects.all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset()[:10]
        serializer = ProductListSerializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def low_stock(self, request):
        """Get low stock products (admin only)"""
        low_stock_products = Product.objects.filter(stock__lt=10, is_active=True)
        serializer = ProductListSerializer(low_stock_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def analytics(self, request):
        """Admin analytics dashboard"""
        from orders.models import Order, OrderItem
        
        # Total revenue
        total_revenue = Order.objects.filter(
            payment_status='success'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Orders by status
        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Top 10 selling products
        top_products = OrderItem.objects.values(
            'product__name', 'product__id'
        ).annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('quantity') * F('price_at_purchase'))
        ).order_by('-total_sold')[:10]
        
        # Low stock products
        low_stock = Product.objects.filter(
            stock__lt=10, 
            is_active=True
        ).values('id', 'name', 'stock', 'category__name')
        
        # Recent orders
        from orders.serializers import OrderListSerializer
        recent_orders = Order.objects.all().order_by('-created_at')[:10]
        
        return Response({
            'total_revenue': float(total_revenue),
            'orders_by_status': list(orders_by_status),
            'top_products': list(top_products),
            'low_stock_products': list(low_stock),
            'recent_orders': OrderListSerializer(recent_orders, many=True).data,
            'total_products': Product.objects.count(),
            'total_categories': Category.objects.count(),
        })