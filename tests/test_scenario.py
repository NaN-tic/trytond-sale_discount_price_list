from decimal import Decimal
import unittest
from proteus import Model
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.modules.account.tests.tools import create_chart, get_accounts
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
        company = get_company()

        # Create chart of accounts::
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create parties
        Party = Model.get('party.party')
        party = Party(name="Party")
        party.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')

        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('50')
        template.account_category = account_category
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
        self.assertEqual(sale.untaxed_amount, Decimal('8.00'))

        # Modify Header

        sale = Sale()
        sale.party = party
        sale.price_list = None
        line = sale.lines.new()
        line.product = product
        line.quantity = 1
        self.assertEqual(line.base_price, Decimal('50.0000'))
        self.assertEqual(line.discount_amount, Decimal('0.0000'))
        self.assertEqual(line.discount, None)
        sale.save()
        self.assertEqual(sale.untaxed_amount, Decimal('50.00'))

        modify_header = sale.click('modify_header')
        modify_header.form.party == party
        modify_header.form.price_list = price_list
        modify_header.execute('modify')

        line, = sale.lines
        self.assertEqual(line.base_price, Decimal('10.0000'))
        self.assertEqual(line.discount_amount, Decimal('1.0000'))
        self.assertEqual(line.discount, '10%')
        self.assertEqual(sale.untaxed_amount, Decimal('9.00'))
