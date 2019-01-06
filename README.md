## Flask Rest API Example - Online Store

I started working on this after taking a Udemy course. I'm mimmicking the Shopify API for practice.
https://www.udemy.com/restful-api-flask-course/
https://help.shopify.com/en/api/reference



# Product
original issue: https://github.com/chipmyersjr/flask_rest_api/issues/1

**Fields:**
* id
* title
* product_type
* vendor
* store_id
* created_at
* updated_at
* deleted_at

**Methods:**
* GET /products/  (Retrieves a list of products)
* GET /products/count/   (Retrieves a count of products)
* GET /products/{product_id}   (Retrieves a single product)
* POST /products/   (Creates a new product)
* PUT /products/{product_id}   (Updates a product)
* DELETE /admin/products/{product_id}   (Deletes a product)


# Store
original issue: https://github.com/chipmyersjr/flask_rest_api/issues/2

**Fields:**
* id
* name
* tagline
* app_id
* app_secret
* created_at
* updated_at
* deleted_at

**Methods:**
* GET /store/  (Retrieves current store based on APP-ID)
* POST /store/   (Creates a new store)
* POST /store/token/ (Creates a new access token for store)
* PUT /store/   (Updates store based on APP-ID)
* DELETE /store/ (Deletes a store based on APP-ID)
* DELETE /admin/products/#{product_id}   (Deletes a product)
