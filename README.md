# Product Service (API1)

## Endpoints

### 1. all products

- **GET** `/api/v1/product/`  
  **Response**
  ```json
  [
    {
      "id": "integer",
      "sell_price": "decimal",
      "name": "string",
      "image": "string (URL) or null",
      "description": "string",
      "price": "decimal",
      "available": "boolean",
      "created": "datetime (ISO 8601)",
      "updated": "datetime (ISO 8601)",
      "discount": "decimal",
      "category": "integer"
    }
  ]
  ```

### 2. specific product

- **GET** `/api/v1/product/{pk}/`  
  **Response**
  ```json
  {
    "id": "integer",
    "sell_price": "decimal",
    "name": "string",
    "image": "string (URL) or null",
    "description": "string",
    "price": "decimal",
    "available": "boolean",
    "created": "datetime (ISO 8601)",
    "updated": "datetime (ISO 8601)",
    "discount": "decimal",
    "category": "integer"
  }
  ```

### 3. **Product Search & Filtering**

You can filter and search products using the following query parameters:

- `?search=` – Search by product name (case insensitive).
- `?price_min=` – Filter by minimum selling price.
- `?price_max=` – Filter by maximum selling price.
- `?discount_min=` – Filter by minimum discount percentage.
- `?discount_max=` – Filter by maximum discount percentage.
- `?available=` – Filter by availability (`True` or `False`).

You can combine these parameters for advanced filtering.

Works with the following endpoints:

- **All Products:**  
  `GET /api/v1/product/`

- **Products by Category:**  
  `GET /api/v1/category/{pk}/products/`

### 1. all categories

- **GET** `/api/v1/category/`  
  **Response**
  ```json
  [
    {
      "id": "integer",
      "name": "string"
    }
  ]
  ```

### 2. specific categoty

- **GET** `/api/v1/category/{pk}/`  
  **Response**
  ```json
  {
    "id": "integer",
    "name": "string"
  }
  ```

### 3. products by category

- **GET** `/api/v1/category/{pk}/products/`  
  **Response**
  ```json
  [
    {
      "id": "integer",
      "sell_price": "decimal",
      "name": "string",
      "image": "string or null",
      "description": "string",
      "price": "decimal",
      "available": "boolean",
      "created": "datetime",
      "updated": "datetime",
      "discount": "decimal",
      "category": "integer"
    }
  ]
  ```

### **Create, update, delete products and category for Admin(is_staff) from user service**

- **POST** `/api/v1/product/`
- **PUT** `/api/v1/product/{pk}/`
- **DELETE** `/api/v1/product/{pk}/`
- **POST** `/api/v1/category/`
- **PUT** `/api/v1/category/{pk}`
- **DELETE** `/api/v1/category/{pk}`

# Cart Service (API2)

## Endpoints

### 1. Get Cart

- **GET** `/api/v1/cart/get_cart/`
- **Response**:
  ```json
  {
    "cart_details": [
      {
        "product_id": "string",
        "name": "string",
        "price": "decimal",
        "discount": "decimal",
        "quantity": "integer",
        "image": "string",
        "price_after_discount:": "decimal",
        "price_per_item": "decimal"
      }
    ],
    "total_price": "decimal",
    "cart_key": "string"
  }
  ```

### 2. Add Item to Cart

- **POST** `/api/v1/cart/add_item/`
- **Request Body**:
  ```json
  {
    "product_id": "string",
    "quantity": "integer"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Item added to cart",
    "product_id": "string",
    "quantity": "integer",
    "name": "string",
    "price": "decimal",
    "discount": "decimal"
  }
  ```

### 3. Remove Item from Cart

- **DELETE** `/api/v1/cart/remove_item/`
- **Request Body**:
  ```json
  {
    "product_id": "string"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Item removed from cart",
    "product_id": "string"
  }
  ```

### 4. Clear Cart

- **DELETE** `/api/v1/cart/clear_cart/`
- **Response**:
  ```json
  {
    "message": "Cart cleared"
  }
  ```

### 5. Update Item Quantity

- **PATCH** `/api/v1/cart/update_quantity/`
- **Request Body**:
  - To set a specific quantity:
    ```json
    {
      "product_id": "string",
      "quantity": "integer"
    }
    ```
  - To change by a value (e.g., +1, -1):
    ```json
    {
      "product_id": "string",
      "change": "integer"
    }
    ```
- **Response**:
  ```json
  {
    "message": "Quantity updated successfully.",
    "product_id": "string",
    "new_quantity": "integer"
  }
  ```

### 6. Get User Cart only for ANOTHER SERVICE

- **GET** `/api/v1/cart/get_user_cart/`
- **Request Parameters**:
  ```json
  {
    "cart_key": "string"
  }
  ```
- **Response**:
  ```json
  {
    "cart_details": [
      {
        "product_id": "string",
        "name": "string",
        "price": "decimal",
        "discount": "decimal",
        "quantity": "integer",
        "image": "string",
        "price_after_discount": "decimal",
        "price_per_item": "decimal"
      }
    ],
    "total_price": "decimal"
  }
  ```

### 7. Clear User Cart only for ANOTHER SERVICE

- **DELETE** `/api/v1/cart/clear_user_cart/`
- **Request Body**:
  ```json
  {
    "cart_key": "string"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Cart {cart_key} cleared"
  }
  ```

# Order Service (API3)

## Endpoints

### 1. Create Order

- **POST** `/api/v1/order/create_order/`
- **Request Body**:
  ```json
  {
    "cart_key": "string",
    "shipping_address": "string",
    "city": "string",
    "postcode": "string",
    "first_name": "string",
    "last_name": "string",
    "phone_number": "string",
    "email": "string",
    "notes": "string"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Order created successfully",
    "order_id": "integer",
    "cart_key": "string"
  }
  ```

### 2. Update status(for Admin) and paid(for Service) for order

- **POST** `/api/v1/order/update_order/`
- **Request Body**:
- Admin
  ```json
  {
    "order_id": "integer",
    "status": "string"
  }
  ```
- Service
  ```json
  {
  "order_id": "integer"r,
  "is_paid": true or false,
  "payment_intent": "string",
   "status": "string"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Order updated successfully."
  }
  ```

### 3. Get all Orders authorized user, with Token Authorization

- **GET** `/api/v1/order/get_orders/`
- **Request Parameters**:
- **Response**:
  ```json
  {
    "orders": [
      {
        "order_id": "integer",
        "total_price": "decimal",
        "status": "string",
        "is_paid": "boolean",
        "shipping_address": "string",
        "first_name": "string",
        "last_name": "string",
        "phone": "string",
        "email": "string"
      }
    ]
  }
  ```

### 4. Order by id only for SERVICE

- **POST** `/api/v1/order/{pk}/get_order_by_id/`
- For guest users, cart_key is required to identify the cart.
- For authenticated users, cart_key can be omitted, as the system will use the user_id from token.
- **Request Parameters**:
  ```json
  {
    "cart_key": "string"
  }
  ```
- **Response**:
  ```json
  {
    "order": {
      "order_id": "integer",
      "total_price": "decimal",
      "items": [
        {
          "product_name": "string",
          "quantity": "integer",
          "unit_price": "decimal"
        }
      ]
    }
  }
  ```

# User Service (API4)

## Endpoints

### Register

- **POST** `/api/v1/users/register/`
- **Request Parameters**:
  ```json
  {
    "username": "string",
    "password": "string",
    "confirm_password": "string",
    "email": "string"
  }
  ```
- **Response**:
  ```json
  {
      "message": "User registered successfully.",
      "user": {
          "id": integer,
          "username": "string",
          "email": "string",
          "first_name": "string",
          "last_name": "string",
          "phone_number": "string" or null,
          "city": "string" or null,
          "address":"string" or null,
          "postcode": "string" or null,
          "access":"string",
          "refresh":"string"
      }
  }
  ```

### Login

- **POST** `/api/v1/users/login/`
- **Request Parameters**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "refresh": "string",
    "access": "string"
  }
  ```

### Logout

- **POST** `/api/v1/users/logout/`
- **Request Parameters**:
  ```http
  Authorization: Bearer <your_token_here>
  ```
- **Response**:
  ```json
  {
    "message": "Logged out successfully."
  }
  ```

### Me

- **GET** `/api/v1/users/me/`
- **Request Parameters**:
  ```http
  Authorization: Bearer <your_token_here>
  ```
- **Response**:
  ```json
  {
      "id": integer,
      "username": "string",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "phone_number": "string" or null,
      "city": "string" or null,
      "address":"string" or null,
      "postcode": "string" or null
  }
  ```

### Update

- **PUT** `/api/v1/users/me/update/`
- You can update this information
  ```json
  {
      "username": "string",
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "phone_number": "string" or null,
      "city": "string" or null,
      "address":"string" or null,
      "postcode": "string" or null
  }
  ```

### Change Passwoord

- **POST** `/api/v1/users/me/change-password/`
- **Request Parameters**:
  ```http
  Authorization: Bearer <your_token_here>
  ```
- **Response**:
  ```json
  {
    "old_password": "string",
    "new_password": "string",
    "confirm_password": "string"
  }
  ```

### Reset password with email

- **POST** `/api/v1/users/reset-password/`
- **Request Parameters**:
  ```json
  {
    "email": "string"
  }
  ```
- **Response**:
  ```json
  {
    "detail": "If an account with that email exists, a password reset email has been sent."
  }
  ```
- **POST** `/api/v1/users/reset-password/confirm/?uidb64={UIDB64}&token={TOKEN}` - from email
- **Request Parameters**:
  ```json
  {
    "new_password": "string",
    "confirm_password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "detail": "Password has been reset."
  }
  ```

### Refresh Token

- **POST** `/api/v1/users/token/refresh/`
- **Request Parameters**:
  ```json
  {
    "refresh": "your_refresh_token_here"
  }
  ```
- **Response**:
  ```json
  {
    "access": "new_access_token_here"
  }
  ```

### Verify Token

- **POST** `/api/v1/users/token/verify/`
- **Request Parameters**:
  ```json
  {
    "token": "your_access_token_here"
  }
  ```
- **Response**:
  ```json
  {
    "detail": "Token is valid"
  }
  ```

# Payment Service (API5)

## Endpoints

### 1. Create payment link

- **POST** `/api/v1/payments/create-checkout-session/`
- For guest users, cart_key is required to identify the cart.
- For authenticated users, cart_key can be omitted, as the system will use the user_id from token.
- **Request Parameters**:

  ```json


  ```

- **Response**:
  ```json
  {
    "checkout_url": "string"
  }
  ```
- **After the payment is processed, if successful**:
  ```json
  {
    "status": "success"
  }
  ```
- **If the payment is canceled or failed**:
  ```json
  {
    "status": "canceled"
  }
  ```

# Log Service (API6)

### Writes logs from different microservices to cassandra

# Notifications service (API7)

### Sends request for password recovery, registration, orders, etc. to the email
