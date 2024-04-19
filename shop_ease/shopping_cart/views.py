from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from shopping_cart.models import Order, OrderItem, Payment, Product, User
from shopping_cart.serializer import (
    PaymentSerializer,
    ProductSerializer,
    UserSerializer,
)
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

    @transaction.atomic
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

    @transaction.atomic
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


class ManageOrderAPIView(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            request_body = request.data
            order_obj = Order.objects.create(user=request.user)
            for product_data in request_body.get("products", []):
                product_id = product_data.get("product_id")
                quantity = product_data.get("quantity")
                product = Product.objects.get(pk=product_id)
                OrderItem.objects.create(
                    order=order_obj, product=product, quantity=quantity
                )
            total_price = sum(
                item.product.price * item.quantity
                for item in order_obj.orderitem_set.all()
            )
            order_obj.total_price = total_price
            order_obj.save()
            return Response({"message": "Order created successfully"}, status=201)
        except Product.DoesNotExist:
            return Response(
                {"error": "One or more products do not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, *args, **kwargs):
        try:
            order_id = request.GET.get("order_id")
            if order_id is not None:
                order_obj = Order.objects.get(user=request.user, id=order_id)
                orders = [order_obj]
            else:
                orders = Order.objects.filter(user=request.user)
            response_data = []
            for order in orders:
                order_items = OrderItem.objects.filter(order=order)
                product_details = []
                for item in order_items:
                    product = item.product
                    quantity = item.quantity
                    price = product.price
                    product_details.append(
                        {
                            "product_id": product.id,
                            "product_name": product.product_name,
                            "product_description": product.description,
                            "price": price,
                            "quantity": quantity,
                        }
                    )
                response_data.append(
                    {
                        "order_id": order.id,
                        "user_id": order.user.id,
                        "product_details": product_details,
                        "total_price": order.total_price,
                    }
                )
            return Response(response_data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            request_body = request.data
            order_obj = Order.objects.get(pk=request_body.get("order_id", None))
            existing_order_items = list(order_obj.orderitem_set.all())
            new_order_items = []
            if order_obj:
                for product_data in request_body.get("products", []):
                    product_id = product_data.get("product_id")
                    quantity = product_data.get("quantity")
                    product = Product.objects.get(pk=product_id)
                    order_item = order_obj.orderitem_set.filter(product=product).first()
                    if order_item:
                        order_item.quantity = quantity
                        order_item.save()
                        existing_order_items.remove(order_item)
                    else:
                        new_order_items.append(
                            OrderItem(
                                order=order_obj, product=product, quantity=quantity
                            )
                        )

                for order_item in existing_order_items:
                    order_item.delete()
                for order_item in new_order_items:
                    order_item.save()
                total_price = sum(
                    item.product.price * item.quantity
                    for item in order_obj.orderitem_set.all()
                )
                order_obj.total_price = Decimal(total_price)
                order_obj.save()
                return Response(
                    {"message": "Order updated successfully"}, status=status.HTTP_200_OK
                )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "One or more products do not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ManagePurchaseAPIView(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            request_body = request.data
            order_obj = Order.objects.get(id=request_body.get("order_id", None))
            if order_obj:
                existing_payment = Payment.objects.filter(order=order_obj).first()
                if existing_payment:
                    return Response(
                        {
                            "error": "Payment already exists for the order",
                            "payment_status": f"{existing_payment.payment_status}",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                payment_method = request_body.get("payment_method", None)
                amount_to_paid = request_body.get("amount_paid", None)
                total_amount = order_obj.total_price
                if amount_to_paid == total_amount:
                    Payment.objects.create(
                        order=order_obj,
                        payment_method=payment_method,
                        amount_paid=amount_to_paid,
                        payment_status="Completed",
                    )
                    return Response(
                        {"message": "Payment successful"},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    Payment.objects.create(
                        order=order_obj,
                        payment_method=payment_method,
                        amount_paid=amount_to_paid,
                        payment_status="Failed",
                    )
                    return Response(
                        {
                            "error": "Amount paid does not match total amount. Payment failed."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request, *args, **kwargs):
        try:
            order_id = request.GET.get("order_id")
            if order_id:
                order_obj = Order.objects.get(user=request.user, pk=order_id)
                payment_obj = Payment.objects.get(order=order_obj)
                serializer = PaymentSerializer(payment_obj)
                return Response(serializer.data)
            else:
                payments = Payment.objects.filter(order__user=request.user)
                serializer = PaymentSerializer(payments, many=True)
                return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, *args, **kwargs):
        try:
            request_body = request.data
            order_obj = Order.objects.get(id=request_body.get("order_id", None))
            if order_obj:
                existing_payment = Payment.objects.filter(order=order_obj).first()
                if not existing_payment.payment_status == "Completed":
                    if existing_payment:
                        payment_method = request_body.get("payment_method", None)
                        amount_to_paid = request_body.get("amount_paid", None)
                        total_amount = order_obj.total_price
                        if amount_to_paid == total_amount:
                            existing_payment.payment_method = payment_method
                            existing_payment.payment_status = "Completed"
                            existing_payment.amount_paid = amount_to_paid
                            existing_payment.save()
                            serilizer = PaymentSerializer(existing_payment)
                            return Response(serilizer.data)
                        else:
                            existing_payment.payment_method = payment_method
                            existing_payment.payment_status = "Failed"
                            existing_payment.amount_paid = amount_to_paid
                            existing_payment.save()
                            return Response(
                                {
                                    "error": "Amount paid does not match total amount. Payment failed."
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                else:
                    return Response(
                        {"error": "Payment already completed"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                return Response(
                    {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
