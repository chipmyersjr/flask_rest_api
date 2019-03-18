from customer import Customer


def main():
    counter = 0
    while counter < 15:
        customer = Customer()
        customer.create()
        counter += 1


if __name__ == "__main__":
    main()