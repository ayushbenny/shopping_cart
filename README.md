# Shopping Cart Application

Welcome to the Shopping Cart Application! This is a Django-Restframework API's that allows users to manage products, create orders, process payments, and more.

## Overview

The Shopping Cart Application provides the following functionalities:

* User management: Allows users to register, login, and update their profile information.
* Product management: Enables users to add, view, update, and delete products.
* Order management: Allows users to create, view, and update orders, including adding/removing products and updating quantities.
* Payment processing: Allows users to make payments for their orders using different payment methods.

## Requirements

To run this application, you'll need the following installed on your system:

* Python 3.10.12
* Poetry (for managing dependencies)
* Django
* Django REST Framework

## Installation

Follow these steps to set up the Shopping Cart Application:

### Poetry

Poetry is a dependency management tool for Python projects. Follow these steps to install Poetry on your system:

```bash
curl -sSL https://install.python-poetry.org | python -

```

### Verify Installation

To verify that Poetry has been installed successfully, run:

```bash
poetry --version
```

### Clone this repository to your local machine:

```bash
git clone https://github.com/ayushbenny/shopping_cart.git
```

### Navigate to the project directory:

```bash
cd shopping_cart
```

### Set up a virtual environment using Poetry:

```bash
poetry install
```

### Activate the virtual environment:

```bash
poetry shell
```

### Apply migrations to set up the database:

```bash
python manage.py migrate
```

### Run the development server:

```bash
python manage.py runserver
```

# API Documentation

For detailed information on the available API endpoints and how to use them, refer to the [API Documentation](API_Documentation.md) file.
