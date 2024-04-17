from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from shopping_cart.models import User
from shopping_cart.serializer import UserSerializer
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


class FetchUserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, email=request.user.email)
        if user_obj:
            user_serializer = UserSerializer(user_obj)
            return Response(user_serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
