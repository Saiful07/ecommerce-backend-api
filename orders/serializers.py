from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductListSerializer
from accounts.models import Address


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price_at_purchase', 'subtotal')
        read_only_fields = ('id', 'price_at_purchase', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'user_email', 'total_amount', 'status', 
                 'payment_status', 'shipping_address', 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'order_number', 'total_amount', 'created_at', 'updated_at')


class CreateOrderSerializer(serializers.Serializer):
    shipping_address_id = serializers.IntegerField(required=False)
    shipping_address = serializers.CharField(required=False)
    
    def validate(self, attrs):
        # Must provide either address_id or full address text
        if not attrs.get('shipping_address_id') and not attrs.get('shipping_address'):
            raise serializers.ValidationError(
                "Either shipping_address_id or shipping_address must be provided"
            )
        return attrs
    
    def validate_shipping_address_id(self, value):
        request = self.context.get('request')
        if value:
            try:
                address = Address.objects.get(id=value, user=request.user)
            except Address.DoesNotExist:
                raise serializers.ValidationError("Address not found")
        return value


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'total_amount', 'status', 'payment_status', 
                 'items_count', 'created_at')
        read_only_fields = fields
    
    def get_items_count(self, obj):
        return obj.items.count()