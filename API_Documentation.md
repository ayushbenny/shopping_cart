# Add User (POST)

```
Adds a new user to the system.

Endpoint: http://localhost:8000/user/

Request Body (Sample Data):

{
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe123",
    "email": "johndoe@example.com",
    "password": "Password123!",
    "phone_number": "1234567890"
}
```

# Login User (POST)

```
Authenticates and logs in a user.

Endpoint: http://localhost:8000/api/token/

Request Body (Sample Data):

{
    "username": "johndoe123",
    "password": "Password123!"
}
```

# Fetch User (GET)

```
Retrieves user details.

Endpoint: http://localhost:8000/api/user/ -> Token Required
```

# Update User (PUT)

```
Updates user details.

Endpoint: http://localhost:8000/api/user/ -> Token Required

Request Body (Sample Data):


{
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe123",
    "email": "johndoe@example.com",
    "password": "NewPassword456!",
    "phone_number": "1234567890"
}
```

# Update User (PATCH)

```
Updates user password.

Endpoint: http://localhost:8000/api/user/ -> Token Required

Request Body (Sample Data):


{
    "password": "NewPassword456!"
}
```

# Create Product (POST)

```
Adds a new product to the system.

Endpoint: http://localhost:8000/api/product/

Request Body (Sample Data):


{
    "product_name": "Boxing Glove",
    "description": "Premium quality boxing glove",
    "price": 99.99
}
```

# Fetch Product (GET)

```
Retrieves product details.

Endpoint: http://localhost:8000/api/product/?product_name=glove&minimum_price=100&maximum_price=2500

please note: "http://localhost:8000/api/product/?product_name" -> will list out all the Products created
```

# Update Product (PUT)

```
Updates product details.

Endpoint: http://localhost:8000/api/product/

Request Body (Sample Data):


{
    "id": 5,
    "product_name": "Hand Wrapping",
    "description": "Highly durable hand wrapping for boxing",
    "price": 39.99,
    "is_delete": false
}
```

# Update Product (PATCH)

```
Updates product status.

Endpoint: http://localhost:8000/api/product/

Request Body (Sample Data):

{
    "id": 4,
    "is_delete": true
}
```

# Create Order (POST)

```
Creates a new order.

Endpoint: http://localhost:8000/api/order/ -> Token Required

Request Body (Sample Data):


{
    "products": [
        {"product_id": 1, "quantity": 2},
        {"product_id": 2, "quantity": 4},
        {"product_id": 3, "quantity": 3}
    ]
}
```

# Fetch Order (GET)

```
Retrieves order details.

Endpoint: http://localhost:8000/api/order/?order_id=3 -> Token Required

please note: "http://localhost:8000/api/order/" -> it will list out all the Orders created by the requested user.
```

# Update Order (PUT)

```
Updates order details.

Endpoint: http://localhost:8000/api/order/ -> Token Required

Request Body (Sample Data):

{
    "order_id": 2,
    "products": [
        {"product_id": 2, "quantity": 6},
        {"product_id": 3, "quantity": 9},
        {"product_id": 5, "quantity": 1}
    ]
}
```

# Create Payment (POST)

```
Creates a new payment.

Endpoint: http://localhost:8000/api/payment/ -> Token Required

Request Body (Sample Data):


{
    "order_id": 4,
    "payment_method": "Credit Card",
    "amount_paid": 2250.50
}
```

# Fetch Payment (GET)

```
Retrieves payment details.

Endpoint: http://localhost:8000/api/payment/?order_id=3 -> Token Required

please note: "http://localhost:8000/api/payment/" -> This will list out all the payments done by the requested user.
```

# Update Payment (PUT)

```
Updates payment details.

Endpoint: http://localhost:8000/api/payment/ -> Token Required

Request Body (Sample Data):


{
    "order_id": 4,
    "payment_method": "Credit Card",
    "amount_paid": 2250.50
}
```
