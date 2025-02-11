# Product Service (API1)

## Endpoints

### Products

- **List All Products**  
  `GET http://127.0.0.1:8000/api/v1/product/`  
  Returns a list of all products.

- **Product Detail**  
  `GET http://127.0.0.1:8000/api/v1/product/{pk}/`  
  Returns details of a specific product identified by its primary key (`pk`).

- **Product Search & Filtering**
  `GET http://127.0.0.1:8000/api/v1/product/?search= `
  `GET http://127.0.0.1:8000/api/v1/product/?price_min=`
  `GET http://127.0.0.1:8000/api/v1/product/?price_max=`
  `GET http://127.0.0.1:8000/api/v1/product/?discount_min=`
  `GET http://127.0.0.1:8000/api/v1/product/?discount_max=`
  `GET http://127.0.0.1:8000/api/v1/product/?available=`
  You can combine them

### Categories

- **List All Categories**  
  `GET http://127.0.0.1:8000/api/v1/category/`  
  Returns a list of all categories.

- **Category Detail**  
  `GET http://127.0.0.1:8000/api/v1/category/{pk}/`  
  Returns details of a specific category identified by its primary key (`pk`).

- **Products by Category**  
  `GET http://127.0.0.1:8000/api/v1/category/{pk}/products/`  
  Returns a list of products that belong to the specified category.

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
        "quantity": "integer",
        "image": "string",
        "price_per_item": "decimal"
      }
    ],
    "total_price": "decimal"
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
    "price": "decimal"
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
