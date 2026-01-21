from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import razorpay
import hmac
import hashlib
from .models import Payment
from .serializers import (
    PaymentInitiateSerializer, 
    PaymentVerifySerializer,
    PaymentSerializer
)
from orders.models import Order


class PaymentViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    @action(detail=False, methods=['post'])
    def initiate(self, request):
        """Initiate payment with Razorpay"""
        serializer = PaymentInitiateSerializer(
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Create Razorpay order
        razorpay_order_data = {
            'amount': int(order.total_amount * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': order.order_number,
            'payment_capture': 1  # Auto capture
        }
        
        try:
            razorpay_order = self.razorpay_client.order.create(data=razorpay_order_data)
            
            # Create or update payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'razorpay_order_id': razorpay_order['id'],
                    'amount': order.total_amount,
                    'currency': 'INR',
                    'status': 'initiated'
                }
            )
            
            if not created:
                payment.razorpay_order_id = razorpay_order['id']
                payment.status = 'initiated'
                payment.save()
            
            return Response({
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'order_id': order.id,
                'order_number': order.order_number
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Payment initiation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify payment signature"""
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        razorpay_order_id = serializer.validated_data['razorpay_order_id']
        razorpay_payment_id = serializer.validated_data['razorpay_payment_id']
        razorpay_signature = serializer.validated_data['razorpay_signature']
        order_id = serializer.validated_data['order_id']
        
        # Verify signature
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            return Response(
                {'error': 'Invalid payment signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(
                    id=order_id, 
                    user=request.user
                )
                payment = Payment.objects.select_for_update().get(order=order)
                
                # Update payment
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = razorpay_signature
                payment.status = 'success'
                payment.save()
                
                # Update order
                order.payment_status = 'success'
                order.status = 'paid'
                order.save()
                
                return Response({
                    'message': 'Payment verified successfully',
                    'order_number': order.order_number,
                    'payment_status': payment.status
                }, status=status.HTTP_200_OK)
        
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment record not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Payment verification failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @method_decorator(csrf_exempt, name='dispatch')
    @action(detail=False, methods=['post'], permission_classes=[])
    def webhook(self, request):
        """Handle Razorpay webhook"""
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = settings.RAZORPAY_KEY_SECRET
        
        # Verify webhook signature
        try:
            self.razorpay_client.utility.verify_webhook_signature(
                request.body.decode('utf-8'),
                webhook_signature,
                webhook_secret
            )
        except:
            return Response(
                {'error': 'Invalid webhook signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        webhook_body = request.data
        event = webhook_body.get('event')
        
        if event == 'payment.captured':
            payment_entity = webhook_body['payload']['payment']['entity']
            razorpay_payment_id = payment_entity['id']
            
            try:
                payment = Payment.objects.get(razorpay_payment_id=razorpay_payment_id)
                
                with transaction.atomic():
                    payment.status = 'success'
                    payment.gateway_response = str(webhook_body)
                    payment.save()
                    
                    order = payment.order
                    order.payment_status = 'success'
                    order.status = 'paid'
                    order.save()
            
            except Payment.DoesNotExist:
                pass
        
        elif event == 'payment.failed':
            payment_entity = webhook_body['payload']['payment']['entity']
            razorpay_order_id = payment_entity.get('order_id')
            
            try:
                payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                
                with transaction.atomic():
                    payment.status = 'failed'
                    payment.gateway_response = str(webhook_body)
                    payment.save()
                    
                    order = payment.order
                    order.payment_status = 'failed'
                    order.status = 'payment_failed'
                    order.save()
            
            except Payment.DoesNotExist:
                pass
        
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)