from decimal import Decimal
import unittest
from proteus import Model
from trytond.modules.company.tests.tools import create_company
from trytond.tests.tools import activate_modules
from trytond.tests.test_tryton import drop_db


class Test(unittest.TestCase):
    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test_sale_discount(self):
        activate_modules('sale_discount_price_list')

        create_company()

        # Create parties
        Party = Model.get('party.party')
        party = Party(name="Party")
        party.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')

        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('50')
        template.save()
        product, = template.products


        # Create a price list
        PriceList = Model.get('product.price_list')
        price_list = PriceList()
        price_list.name = 'Price List'
        line = price_list.lines.new()
        line.base_price_formula = '10.0'
        line.discount_rate = Decimal('0.1')
        price_list.save()

        # Create a sale
        Sale = Model.get('sale.sale')
        sale = Sale()
        sale.party = party
        sale.price_list = price_list
        line = sale.lines.new()
        line.product = product
        line.quantity = 1
        self.assertEqual(line.base_price, Decimal('10'))
        self.assertEqual(line.discount_rate, Decimal('0.1'))
        self.assertEqual(line.discount_amount, Decimal('1'))
        self.assertEqual(line.discount, '10%')
        self.assertEqual(line.unit_price, Decimal('9'))

        # Set a discount of 10%
        line.discount_rate = Decimal('0.2')
        self.assertEqual(line.unit_price, Decimal('8'))
        self.assertEqual(line.discount_amount, Decimal('2'))
        self.assertEqual(line.discount, '20%')

        sale.save()
        line, = sale.lines
        self.assertEqual(line.unit_price, Decimal('8'))
        self.assertEqual(line.discount_amount, Decimal('2'))
        self.assertEqual(line.discount, '20%')

