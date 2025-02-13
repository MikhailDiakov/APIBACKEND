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
  `GET http://127.0.0.1:8000`  
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
    "first_name": "string",
    "last_name": "string",
    "phone": "string",
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

### 2. Update Order only for ANOTHER SERVICE

- **POST** `/api/v1/order/update_order/`
- **Request Body**:
  ```json
  {
    "order_id": "integer",
    "status": "string",
    "is_paid": "boolean"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Order updated successfully."
  }
  ```

### 3. Get Orders only for ANOTHER SERVICE

- **GET** `/api/v1/order/get_orders/`
- **Request Parameters**:
  ```json
  {
    "cart_key": "string"
  }
  ```
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
