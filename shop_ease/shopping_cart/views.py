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
    """
    API endpoint for registering a new user.

    This endpoint allows users to register with the system by providing
    their user data. Upon successful registration, a new user is created
    and their data is returned.

    Methods:
    - POST: Create a new user with provided data.
    """

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
    """
    API endpoint for managing user data.

    This endpoint allows authenticated users to retrieve and update their own data.

    Methods:
    - GET: Retrieve the data of the currently authenticated user.
    - PUT: Update the data of the currently authenticated user.
    - PATCH: Partially update the data of the currently authenticated user.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieve the data of the currently authenticated user.

        Returns:
        - Response: JSON response with the serialized user data.
        """
        user_obj = get_object_or_404(User, email=request.user.email)
        if user_obj:
            user_serializer = UserSerializer(user_obj)
            return Response(user_serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """
        Update the data of the currently authenticated user.

        This endpoint allows for updating the user's data entirely.

        Returns:
        - Response: JSON response with the updated user data.
        """
        user_obj = get_object_or_404(User, email=request.user.email)
        user_serializer = UserSerializer(user_obj, data=request.data)
        if user_serializer.is_valid():
            if "password" in request.data:
                user_obj.set_password(request.data["password"])
            user_serializer.save()
            return Response(user_serializer.data)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        """
        Partially update the data of the currently authenticated user.

        This endpoint allows for partially updating the user's data.

        Returns:
        - Response: JSON response with the partially updated user data.
        """
        user_obj = get_object_or_404(User, email=request.user.email)
        user_serializer = UserSerializer(user_obj, data=request.data, partial=True)
        if user_serializer.is_valid():
            if "password" in request.data:
                user_obj.set_password(request.data["password"])
            user_serializer.save()
            return Response(user_serializer.data)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageProductAPIView(APIView):
    """
    API endpoint for managing products.

    This endpoint allows for creating, retrieving, updating, and partially updating products.

    Methods:
    - POST: Create a new product.
    - GET: Retrieve products based on optional query parameters.
    - PUT: Update an existing product entirely.
    - PATCH: Partially update an existing product.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Create a new product.

        This endpoint allows for creating a new product by providing the necessary product data.

        Returns:
        - Response: JSON response with the created product data.
        """
        request_body = request.data
        product_serializer = ProductSerializer(data=request_body)
        if product_serializer.is_valid():
            _product_obj = product_serializer.save()
            return Response(product_serializer.data, status=status.HTTP_201_CREATED)
        return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Retrieve products based on optional query parameters.

        This endpoint allows for retrieving products based on various query parameters such as
        product name, minimum price, and maximum price.

        Returns:
        - Response: JSON response with the list of products matching the criteria.
        """
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
        """
        Update an existing product entirely.

        This endpoint allows for updating an existing product entirely with new data.

        Returns:
        - Response: JSON response with the updated product data.
        """
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
        """
        Partially update an existing product.

        This endpoint allows for partially updating an existing product with new data.

        Returns:
        - Response: JSON response with the partially updated product data.
        """
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
    """
    API endpoint for managing orders.

    This endpoint allows users to create, retrieve, and update orders.

    Methods:
    - POST: Create a new order.
    - GET: Retrieve orders for the authenticated user, optionally by order ID.
    - PUT: Update an existing order.
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Create a new order.

        This endpoint allows authenticated users to create a new order by providing product IDs and quantities.

        Returns:
        - Response: JSON response indicating success or failure of the order creation.
        """
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
        """
        Retrieve orders for the authenticated user, optionally by order ID.

        This endpoint allows authenticated users to retrieve their orders. If an order ID is provided,
        only the details of that specific order are returned.

        Returns:
        - Response: JSON response with order details.
        """
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
        """
        Update an existing order.

        This endpoint allows authenticated users to update an existing order by providing new product IDs and quantities.

        Returns:
        - Response: JSON response indicating success or failure of the order update.
        """
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
    """
    API endpoint for managing purchases.

    This endpoint allows users to create, retrieve, and update payments for orders.

    Methods:
    - POST: Create a new payment for an order.
    - GET: Retrieve payments for orders, optionally by order ID.
    - PUT: Update an existing payment for an order.
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Create a new payment for an order.

        This endpoint allows authenticated users to create a new payment for a specific order.

        Returns:
        - Response: JSON response indicating success or failure of the payment creation.
        """
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
        """
        Retrieve payments for orders, optionally by order ID.

        This endpoint allows authenticated users to retrieve payments for their orders.
        If an order ID is provided, details of the payment for that specific order are returned.

        Returns:
        - Response: JSON response with payment details.
        """
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
        """
        Update an existing payment for an order.

        This endpoint allows authenticated users to update an existing payment for an order.

        Returns:
        - Response: JSON response indicating success or failure of the payment update.
        """
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
