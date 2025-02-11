# API1

**API1** is a RESTful API service responsible for managing products and categories. It offers endpoints to retrieve lists, individual details, and filtered results based on various criteria such as price (with discount applied), discount percentage, availability, and more.

## Endpoints

### Products

- **List All Products**  
  `GET http://127.0.0.1:8000/api/v1/product/`  
  Returns a list of all products.

- **Product Detail**  
  `GET http://127.0.0.1:8000/api/v1/product/{pk}/`  
  Returns details of a specific product identified by its primary key (`pk`).

- **Product Search & Filtering**
  `GET http://127.0.0.1:8000//api/v1/product/?search= `
  `GET http://127.0.0.1:8000//api/v1/product/?price_min=`
  `GET http://127.0.0.1:8000//api/v1/product/?price_max=`
  `GET http://127.0.0.1:8000//api/v1/product/?discount_min=`
  `GET http://127.0.0.1:8000//api/v1/product/?discount_max=`
  `GET http://127.0.0.1:8000//api/v1/product/?available=`
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
