import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from customer.tests import CustomerTest
from product.tests import ProductTest
from store.tests import StoreTest
from cart.tests import CartTest
from gift_card.tests import GiftCardTest
from credit.tests import CreditTest
from invoice.tests import InvoiceTest
from orders.tests import OrderTest
from refund.tests import RefundTest


if __name__ == "__main__":
    unittest.main()