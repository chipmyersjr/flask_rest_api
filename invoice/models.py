from application import db
from datetime import datetime
import uuid
from collections import Counter

from customer.models import Customer
from cart.models import Cart
from cart.models import CartItem
from product.models import Product
from product.templates import products_obj
from store.models import Store
from utils import paginated_results


class IncorrectDateFormat(Exception):
    pass


class Invoice(db.Document):
    invoice_id = db.StringField(db_field="invoice_id", primary_key=True)
    customer = db.ReferenceField(Customer, db_field="customer_id")
    cart = db.ReferenceField(Cart, db_field="cart_id")
    state = db.StringField(default="open")
    gift_card_used_amount_in_cents = db.IntField(default=0)
    credit_used_amount_in_cents = db.IntField(default=0)
    created_at = db.DateTimeField(default=datetime.now())
    closed_at = db.DateTimeField()

    meta = {
        'indexes': [('customer', ), ('cart', )]
    }

    def create_invoice_line_items(self):
        invoice_line_items = []
        for cart_item in self.cart.get_cart_items():
            invoice_line_item = InvoiceLineItem(
                                    invoice_line_item_id=str(uuid.uuid4().int),
                                    invoice=self,
                                    cart_item=cart_item,
                                    product=cart_item.product_id,
                                    quantity=cart_item.quantity,
                                    unit_amount_in_cents=cart_item.product_id.sale_price_in_cents,
                                    total_amount_in_cents=cart_item.product_id.sale_price_in_cents*cart_item.quantity,
                                    type="item"
                                )
            invoice_line_items.append(invoice_line_item)
            invoice_line_item.invoice_created_at = datetime.now()
            invoice_line_item.save()

        return invoice_line_items

    def get_total_amount(self):
        """
        returns the sum of total amount of invoice line items
        """
        invoice_line_items = InvoiceLineItem.objects.filter(invoice=self).all()
        return sum([invoice_line_item.total_amount_in_cents for invoice_line_item in invoice_line_items])

    def get_tax_amount(self):
        """
        returns the sum of tax amount of invoice line items
        """
        invoice_line_items = InvoiceLineItem.objects.filter(invoice=self).all()
        return sum([invoice_line_item.tax_amount_in_cents for invoice_line_item in invoice_line_items])

    def get_subtotal_amount(self):
        """
        returns invoice subtotal

        total_amount + tax_amount - gift_card_used_amount - credit_used_amount
        """
        return self.get_total_amount() - self.gift_card_used_amount_in_cents - self.credit_used_amount_in_cents \
               + self.get_tax_amount()

    def get_pre_tax_amount(self):
        """
        returns invoice pre tax amount

        total_amount - gift_card_used_amount - credit_used_amount
        """
        return self.get_total_amount() - self.gift_card_used_amount_in_cents - self.credit_used_amount_in_cents

    @classmethod
    def get_all_invoices(cls, request):
        """
        :param request: request object to get current store and query params
        :return: BaseQuerySet object of all invoices for store
        """
        store = Store.objects.filter(app_id=request.headers.get('APP-ID'), deleted_at=None).first()

        customers = Customer.objects.filter(store_id=store)
        invoices = Invoice.objects.filter(customer__in=customers)

        if 'closed' not in request.args:
            invoices = invoices.filter(state="open")
        else:
            if request.args.get("closed").lower() != "true":
                invoices = invoices.filter(state="open")

        if "startdate" in request.args:
            try:
                start = datetime.strptime(request.args.get("startdate"), "%Y%m%d")
                invoices = invoices.filter(created_at__gt=start)
            except ValueError:
                raise IncorrectDateFormat

        if "enddate" in request.args:
            try:
                end = datetime.strptime(request.args.get("enddate"), "%Y%m%d")
                invoices = invoices.filter(created_at__lt=end)
            except ValueError:
                raise IncorrectDateFormat

        return invoices

    meta = {
        'indexes': [('customer', ), ('invoice_id', ), ('cart', )]
    }

    @classmethod
    def get_top_N_products(cls, customer, num_items, request):
        """
        returns the top 10 products purchased by customer

        :param customer: customer of note
        :return: Produce query object
        """
        invoices = Invoice.objects.filter(customer=customer, state="collected")
        invoice_line_items = InvoiceLineItem.objects.filter(invoice__in=invoices).all()

        products = {}
        for invoice_line_item in invoice_line_items:
            if invoice_line_item.product.product_id in products.keys():
                products[invoice_line_item.product.product_id] += invoice_line_item.quantity
            else:
                products[invoice_line_item.product.product_id] = invoice_line_item.quantity

        product_counts = dict(Counter(products).most_common(num_items))

        results = Product.objects.filter(product_id__in=product_counts.keys())
        results = paginated_results(objects=results, collection_name='product', request=request
                                    , per_page=10, serialization_func=products_obj, dictionary=True)

        for product in results["products"]:
            product["num_ordered"] = product_counts[product["product_id"]]

        return sorted(results["products"], key=lambda product: product["num_ordered"], reverse=True)

    def get_invoice_line_items(self):
        """
        returns all line items for invoice

        :return: collection of invoice line item objects
        """
        return InvoiceLineItem.objects.filter(invoice=self).all()


class InvoiceLineItem(db.Document):
    invoice_line_item_id = db.StringField(db_field="invoice_line_item_id", primary_key=True)
    invoice = db.ReferenceField(Invoice, db_field="invoice_id")
    cart_item = db.ReferenceField(CartItem, db_field="cart_item_id")
    product = db.ReferenceField(Product, db_field="product_id")
    quantity = db.IntField()
    unit_amount_in_cents = db.IntField()
    total_amount_in_cents = db.IntField()
    tax_amount_in_cents = db.IntField(default=0)
    type = db.StringField()

    meta = {
        'indexes': [('invoice',)]
    }