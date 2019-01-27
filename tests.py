import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from customer.tests import CustomerTest
from product.tests import ProductTest
from store.tests import StoreTest
from cart.tests import CartTest


if __name__ == "__main__":
    unittest.main()