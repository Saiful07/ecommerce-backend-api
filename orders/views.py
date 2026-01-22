from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer, OrderListSerializer
from carts.models import Cart
from products.models import Product
from accounts.models import Address


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().prefetch_related('items__product')
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create order from cart"""
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        shipping_address_id = serializer.validated_data.get('shipping_address_id')
        shipping_address_text = serializer.validated_data.get('shipping_address')
        
        if shipping_address_id:
            address = Address.objects.get(id=shipping_address_id, user=request.user)
            shipping_address = f"{address.street_address}, {address.city}, {address.state}, {address.postal_code}, {address.country}"
        else:
            shipping_address = shipping_address_text
        
        try:
            with transaction.atomic():
                total_amount = 0
                cart_items = cart.items.select_related('product').select_for_update()
                
                for cart_item in cart_items:
                    product = cart_item.product
                    
                    if product.stock < cart_item.quantity:
                        raise ValueError(
                            f"Insufficient stock for {product.name}. Available: {product.stock}, Requested: {cart_item.quantity}"
                        )
                    
                    total_amount += product.price * cart_item.quantity
                
                order = Order.objects.create(
                    user=request.user,
                    total_amount=total_amount,
                    shipping_address=shipping_address,
                    status='pending',
                    payment_status='pending'
                )
                
                for cart_item in cart_items:
                    product = cart_item.product
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=cart_item.quantity,
                        price_at_purchase=product.price
                    )
                    
                    product.stock -= cart_item.quantity
                    product.save()
                
                cart.items.all().delete()
                
                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order and restore stock"""
        order = self.get_object()
        
        if order.status not in ['pending', 'payment_failed']:
            return Response(
                {'error': 'Only pending or failed orders can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            for order_item in order.items.select_for_update():
                product = order_item.product
                product.stock += order_item.quantity
                product.save()
            
            order.status = 'cancelled'
            order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status (admin only)"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Valid options: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def sales_report(self, request):
        """Sales report with date filtering"""
        from django.utils import timezone
        from datetime import timedelta
        
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        orders = Order.objects.filter(
            created_at__gte=start_date,
            payment_status='success'
        )
        
        daily_sales = orders.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('day')
        
        return Response({
            'period_days': days,
            'total_orders': orders.count(),
            'total_revenue': orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'daily_breakdown': list(daily_sales)
        })