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
* sale_price_in_cents
* created_at
* updated_at
* deleted_at

**Methods:**
* GET /product/  (Retrieves a list of products)
* GET /product/count/   (Retrieves a count of products)
* GET /product/{product_id}   (Retrieves a single product)
* GET /product/search/<query>   (Full-text search of products)    params={available}
* POST /product/   (Creates a new product)
* PUT /product/{product_id}   (Updates a product)
* DELETE /admin/products/{product_id}   (Deletes a product)
* PUT /product/{product_id}/inventory   (Add to, Subtract From, or Set inventory amount)
* POST /product/<product_id>/tag/<tag>  (Creates a new tag)
* DELETE /product/<product_id>/tag/?tag=<tag>     (Removes tag)
* DELETE /product/<product_id>/tag/  (Removes all tags)


# Store
original issue: https://github.com/chipmyersjr/flask_rest_api/issues/2

**Fields:**
* id
* name
* tagline
* app_id
* app_secret
* credit_order_preference
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

*email:*
* email_id
* email
* is_primary
* created_at
* updated_at
* deleted_at

**Methods:**
* GET /customers/      (Retrieves a list of customers)
* GET /customers/{customer-id}      (Retrieves a single customer)
* POST /customers/      (Creates a customer)
* PUT /customers/{customer-id}    (Updates a customer)
* DELETE /customers/{customer-id}    (Deletes a customer)
* GET /customers/count/         (Retrieves a count of customers)
* GET /customer/{customer-id}/address?is_primary=true  (Returns primary address or all customer addresses)
* POST /customer/{customer-id}/address  (Create a new address for customer. Can override is_primary.)
* PUT /customer/{customer-id}/address/{address-id}/make_primary   (Mark address as primary)
* DELETE /customer/{customer-id}/address/{address-id}   (Delete customer address)
* PUT /customer/login   (Logs customer in)
* PUT /customer/logout   (Logs customer out)
* POST /customer/<customer_id>/email/<email_address>?is_primary=false    (Creates a new email for customer)
* DELETE /customer/<customer_id>/email         (Soft deletes email)
* PUT /customer/<customer_id>/email/<email_address>/make_primary    (Makes email address given primary email)
* GET /customer/<customer_id>/snapshot  (Extended customer object)
* PUT /customer/<customer_id>/send_confirmation/   (Send Confirmation email to user)
* PUT /customer/confirm/<token>  (Confirm customer)

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


# Gift Card

original issue = https://github.com/chipmyersjr/flask_rest_api/issues/25

**fields:**

*gift_card*
* gift_card_id
* gifter_customer
* recipient_customer
* original_balance_in_cents 
* current_balance_in_cents
* created_at
* updated_at

*gift_card_spend*
* gift_card_spend_id
* gift_card
* amount
* remaining_balance 
* created_at

**Methods:**
* GET /giftcard/     (Return a list of gift cards)  params = giftercustomerid, recipientcustomerid, active
* GET /giftcard/<gift_card_id>   (Returns specific giftcard)
* GET /customer/<customer_id>/giftcards  (Returns gift cards for customer)   params = active
* POST /giftcard/    (Creates a gift card)


# Credit

original issue = https://github.com/chipmyersjr/flask_rest_api/issues/28

**fields:**

*credit:*
* credit_id
* customer_id
* original_balance
* current_balance
* created_at
* updated_at
* voided_at

*credit_redemption:*
* credit_redemption_id
* credit_id
* invoice_id
* amount
* remaining_balance
* created_at

**Methods:**
* POST /customer/{customer-id}/credit/{amount}   (Issue customer a credit)
* DELETE /customer/{customer-id}/credit/{credit_id} (Void customer credit)
* GET /customer/{customer-id}/credit?active=true   (Get customer credits)


# Invoice

original issue = https://github.com/chipmyersjr/flask_rest_api/issues/17

**fields:**

*invoice:*
* invoice_id
* customer_id
* cart_id
* state [open, collected, failed, refunded, partially refunded]
* created_at
* closed_at

*invoice_line_item:*
* invoice_line_item_id
* invoice_id
* cart_item_id
* product_id
* quantity
* unit_amount_in_cents
* total_amount_in_cents
* tax_amount_in_cents
* type [shipping, item]

**Methods:**
* POST /customer/{customer-id}/cart/billcart   (Bills for all items in customer cart.)
* GET /invoice/{invoice-id}          (Return a single invoices)
* GET /invoice/?closed=false&startdate=19000101&enddate=30000101        (Return all open invoices.)
* GET /customer/{customer_id}/invoices?closed=false           (Get all invoices for a customer)
* POST /invoice/{invoice-id}/collected     (Mark an invoice as collected)
* PUT /invoice/{invoice-id}/failed     (Mark an invoice as failed)
* POST /invoice/{invoice-id}/refund?full=true&credit=false&amount=0 (Refund an Invoice) body_params={line_item_it, amount}
* PUT /invoice/{invoice-id}/refund/close  (Mark a refund as closed)

# Order

original issue = https://github.com/chipmyersjr/flask_rest_api/issues/21

**fields:**

*order:*
* order_id
* store_id
* invoice_id
* status[pending, shipped, delivered, canceled]
* created_at
* shipped_at
* delivered_at
* canceled_at

*order_line_item:*
* order_line_item_id
* order_id
* invoice_line_item_id
* product_id
* quantity

**Methods:**
* GET /order/{order-id}   (Return info on order)
* GET /order/ (Return a list of orders) params = status, created_at_startdate, delivered_at_startdate, canceled_at_startdate, shipped_at_startdate, created_at_enddate, delivered_at_enddate, canceled_at_enddate, shipped_at_enddate
* PUT /order/{order-id}/shipped  (Mark an order as shipped)
* PUT /order/{order-id}/delivered  (Mark an order as delivered)
* PUT /order/{order-id}/canceled   (Mark an order as canceled)
* GET /customer/{customer-id}/orders  (Returns list of orders for a customer) params = status, created_at_startdate, delivered_at_startdate, canceled_at_startdate, shipped_at_startdate, created_at_enddate, delivered_at_enddate, canceled_at_enddate, shipped_at_enddate

# Coupon Code

**fields:**

*coupon_code:*
* coupon_code_id
* store_id
* code
* style [dollars_off, percent_off]
* amount (should be between 0 and 100 if percent_off)
* created_at
* updated_at
* expires_at
* voided_at

*coupon_code_redemption:*
* coupon_code_redemption_id
* coupon_code_id
* invoice_id
* amount
* created_at

**Methods:**
* GET /coupon_code//is_valid    (Check if coupon code exists and is still valid)
* POST /coupon_code/?expires_at=201903150800&style=percent_off&amount=5   (Creates a new coupon code)
* DELETE /coupon_code/     (Voids a coupon code)



# Streaming
MongoDB change events are streamed using Kafka. Spark Streaming is used to calcuate near realtime metrics. Metrics are stored/retrieved with Redis

original issue =  https://github.com/chipmyersjr/flask_rest_api/issues/59, https://github.com/chipmyersjr/flask_rest_api/issues/53

* GET /streaming/toptencartitems/<N>    (Top N items added to cart in current day)
