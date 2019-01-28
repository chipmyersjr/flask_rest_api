## Flask Rest API Example - Online Store

I started working on this after taking a Udemy course. I'm mimmicking the Shopify API for practice.
https://www.udemy.com/restful-api-flask-course/
https://help.shopify.com/en/api/reference



# Product
original issue: https://github.com/chipmyersjr/flask_rest_api/issues/1

Query String Parameters:
vendor  (Filter by vendor)
producttype (Filter by product_type)

**Fields:**
* id
* title
* product_type
* vendor
* store_id
* inventory
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
* PUT /product/{product_id}/inventory   (Add to, Subtract From, or Set inventory amount)


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



# Customer
original issue: https://github.com/chipmyersjr/flask_rest_api/issues/12

**fields:**

*customer:*
* customer_id
* currency
* email
* firstname
* lastname
* total_spent
* last_order_date
* created_at
* updated_at
* deleted_at

*address:*
* address_id
* street
* city
* zip
* state
* country
* is_primary
* created_at
* updated_at
* deleted_at

**Methods:**
* GET /admin/customers      (Retrieves a list of customers)
* GET /admin/customers/{customer-id}      (Retrieves a single customer)
* POST /admin/customers      (Creates a customer)
* PUT /admin/customers/{customer-id}    (Updates a customer)
* DELETE /admin/customers/{customer-id}    (Deletes a customer)
* GET /admin/customers/count/         (Retrieves a count of customers)


# Cart
original issue: https://github.com/chipmyersjr/flask_rest_api/issues/15

**fields:**

*cart:*
* cart_id
* customer_id
* state {open, closed, billed}
* created_at
* last_item_added_at
* invoice_created_at
* closed_at
* deleted_at

*cart_item*
* cart_item_id
* cart_id
* product_id
* quantity
* added_at
* removed_at
* invoice_created_at

**Methods:**
* GET /customer/{customer-id}/cart    (Return customer cart)
* POST /customer/{customer-id}/cart    (Create a new cart - Close Exisiting Cart)
* POST /customer/{customer-id}/cart/item/{product-id}     (Add an item to the cart)
* POST /customer/{customer-id}/cart/item    (Add a batch of items to the cart)
* PUT /customer/{customer-id}/cart/item/{product-id}    (Update quantity of cart item)
* DELETE /customer/{customer-id}/cart   (Closes customer cart)
* DELETE /customer/{customer-id}/cart/item/{product-id}   (Removes item from cart)
* DELETE /customer/{customer-id}/cart/item         (Removes a batch of items from cart)
