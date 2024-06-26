import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.

    Attributes:
    - first_name: First name of the user.
    - last_name: Last name of the user.
    - email: Email address of the user (unique).
    - user_id: Unique identifier for the user (UUID).
    - phone_number: Phone number of the user.
    - is_active: Boolean indicating if the user is active.
    - is_delete: Boolean indicating if the user is deleted.
    - created_at: Date and time when the user was created.
    - updated_at: Date and time when the user was last updated.
    """

    first_name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )
    last_name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )
    email = models.EmailField(unique=True)
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(
        max_length=15,
    )
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User -> {self.email}"


class Product(models.Model):
    """
    Model representing a product.

    Attributes:
    - product_name: Name of the product.
    - description: Description of the product (optional).
    - price: Price of the product.
    - is_delete: Boolean indicating if the product is deleted.
    - created_at: Date and time when the product was created.
    - updated_at: Date and time when the product was last updated.
    """

    product_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Product -> {self.product_name}"


class Order(models.Model):
    """
    Model representing an order.

    Attributes:
    - user: User who placed the order.
    - products: Many-to-many relationship with products through OrderItem.
    - total_price: Total price of the order.
    - created_at: Date and time when the order was created.
    - updated_at: Date and time when the order was last updated.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderItem")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order -> {self.user.email}"


class OrderItem(models.Model):
    """
    Model representing an item within an order.

    Attributes:
    - order: Order to which the item belongs.
    - product: Product in the order.
    - quantity: Quantity of the product in the order.
    - created_at: Date and time when the order item was created.
    - updated_at: Date and time when the order item was last updated.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem -> {self.product.product_name}"


class Payment(models.Model):
    """
    Model representing a payment for an order.

    Attributes:
    - order: Order for which the payment is made.
    - payment_method: Method used for payment.
    - transaction_id: Unique identifier for the payment transaction.
    - amount_paid: Amount paid for the order.
    - payment_status: Status of the payment (Pending/Completed/Failed).
    - created_at: Date and time when the payment was created.
    - updated_at: Date and time when the payment was last updated.
    """

    PAYMENT_STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    )
    PAYMENT_METHOD_CHOICES = (
        ("Credit Card", "Credit Card"),
        ("Wire Transfer", "Wire Transfer"),
        ("Net Banking", "Net Banking"),
        ("UPI", "UPI"),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.id}"
