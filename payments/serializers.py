from rest_framework import serializers
from .models import Payment
from orders.models import Order


class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    
    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value, user=self.context['request'].user)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        
        if order.payment_status == 'success':
            raise serializers.ValidationError("Order already paid")
        
        if order.status == 'cancelled':
            raise serializers.ValidationError("Cannot pay for cancelled order")
        
        return value


class PaymentVerifySerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
    order_id = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = ('id', 'order', 'order_number', 'razorpay_order_id', 'razorpay_payment_id',
                 'amount', 'currency', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')