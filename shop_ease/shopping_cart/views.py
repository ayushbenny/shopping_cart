from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from shopping_cart.models import Product, User
from shopping_cart.serializer import ProductSerializer, UserSerializer
from rest_framework.permissions import AllowAny


class RegisterUserAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            _ = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageUserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, email=request.user.email)
        if user_obj:
            user_serializer = UserSerializer(user_obj)
            return Response(user_serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, email=request.user.email)
        user_serializer = UserSerializer(user_obj, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, email=request.user.email)
        user_serializer = UserSerializer(user_obj, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageProductAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        request_body = request.data
        product_serializer = ProductSerializer(data=request_body)
        if product_serializer.is_valid():
            _product_obj = product_serializer.save()
            return Response(product_serializer.data, status=status.HTTP_201_CREATED)
        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        product_name = request.GET.get("product_name", None)
        minimum_price = request.GET.get("minimum_price", None)
        maximum_price = request.GET.get("maximum_price", None)
        query = Product.objects.filter(is_delete=False).all()
        if product_name:
            query = query.filter(product_name__icontains=product_name)
        if minimum_price:
            query = query.filter(price__gte=minimum_price)
        if maximum_price:
            query = query.filter(price__lte=maximum_price)
        if query.exists():
            product_serializer = ProductSerializer(query, many=True)
            return Response(product_serializer.data)
        else:
            return Response(
                {"message": "No products found matching the criteria."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, *args, **kwargs):
        request_body = request.data
        product_obj = get_object_or_404(Product, id=request_body.get("id"))
        if product_obj:
            serializer = ProductSerializer(product_obj, data=request_body)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "No products found matching the criteria."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def patch(self, request, *args, **kwargs):
        request_body = request.data
        product_obj = get_object_or_404(Product, id=request_body.get("id"))
        if product_obj:
            serializer = ProductSerializer(product_obj, data=request_body, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "No products found matching the criteria."},
            status=status.HTTP_404_NOT_FOUND,
        )
