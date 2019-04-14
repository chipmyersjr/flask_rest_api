from random import randint, choice

from customer_sim import CustomerSim
from admin import Admin


def main():
    adding_cart_items()


def adding_cart_items():
    print("---adding products---")
    product_ids = create_products()

    print("---adding customers---")
    customers = create_customers()

    print("---cart activity---")
    for customer in customers:
        customer.open_cart()
        for _ in range(randint(1, 5)):
            customer.add_cart_item(choice(product_ids))


def create_customers():
    counter = 0
    customers = []
    while counter < 100:
        try:
            customer = CustomerSim()
            customer.create()
            customers.append(customer)
            counter += 1
        except:
            counter += 1
            continue

    return customers


def create_products():
    counter = 0
    admin = Admin()
    product_ids = []
    while counter < 5:
        product_ids.append(admin.create_product().get("product")["product_id"])
        counter += 1

    return product_ids


if __name__ == "__main__":
    main()