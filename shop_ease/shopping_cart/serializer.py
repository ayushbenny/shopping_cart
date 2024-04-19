from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from shopping_cart.models import Order, Payment, Product, User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User instance
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "phone_number",
            "is_active",
            "is_delete",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        try:
            validate_password(password=validated_data.get("password"), user=user)
        except ValidationError as err:
            raise serializers.ValidationError({"password": err.messages})
        return user

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
            try:
                validate_password(
                    password=validated_data.get("password"), user=instance
                )
            except ValidationError as err:
                raise serializers.ValidationError({"password": err.messages})
        return super().update(instance, validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "product_name", "description", "price", "is_delete"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "payment_method",
            "transaction_id",
            "amount_paid",
            "payment_status",
        ]
