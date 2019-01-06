import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from product.tests import ProductTest
from store.tests import StoreTest

if __name__ == '__main__':
    unittest.main()
