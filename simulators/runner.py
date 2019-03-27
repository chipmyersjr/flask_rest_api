from random import randint, choice

from customer import Customer
from admin import Admin


def main():
    product_ids = create_products()
    customers = create_customers()

    for customer in customers:
        customer.open_cart()
        for _ in range(randint(1, 5)):
            customer.add_cart_item(choice(product_ids))


def create_customers():
    counter = 0
    customers = []
    while counter < 100:
        customer = Customer()
        customer.create()
        customers.append(customer)
        counter += 1

    return customers


def create_products():
    counter = 0
    admin = Admin()
    product_ids = []
    while counter < 25:
        product_ids.append(admin.create_product().get("product")["product_id"])
        counter += 1

    return product_ids


if __name__ == "__main__":
    main()