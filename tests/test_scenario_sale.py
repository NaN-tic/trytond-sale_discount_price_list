import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import \
    set_fiscalyear_invoice_sequences
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install sale_discount_price_list
        config = activate_modules('sale_discount_price_list')

        # Create company
        _ = create_company()
        company = get_company()

        # Create sale user
        User = Model.get('res.user')
        Group = Model.get('res.group')
        sale_user = User()
        sale_user.name = 'Sale'
        sale_user.login = 'sale'
        sale_group, = Group.find([('name', '=', 'Sales')])
        sale_user.groups.append(sale_group)
        sale_user.save()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create price list
        PriceList = Model.get('product.price_list')
        price_list = PriceList()
        price_list.name = 'Default List'
        price_list_line = price_list.lines.new()
        price_list_line.discount1 = Decimal('.5')
        price_list_line.discount2 = Decimal('.2')
        price_list_line.discount3 = Decimal('.1')
        price_list.save()

        # Create parties
        Party = Model.get('party.party')
        customer = Party(name='Customer')
        customer.sale_price_list = price_list
        customer.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        product = Product()
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.cost_price_method = 'fixed'
        template.account_category = account_category
        template.save()
        product.template = template
        product.save()

        # Check discounts and unit_price
        config.user = sale_user.id
        Sale = Model.get('sale.sale')
        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale.price_list = price_list
        sale_line = sale.lines.new()
        sale_line.product = product
        sale_line.quantity = 1.0
        self.assertEqual(sale_line.discount1, Decimal('0.5'))
        self.assertEqual(sale_line.discount2, Decimal('0.2'))
        self.assertEqual(sale_line.discount3, Decimal('0.1'))
        self.assertEqual(sale_line.unit_price, Decimal('3.6000'))
        self.assertEqual(sale_line.amount, Decimal('3.6000'))
        self.assertNotEqual(sale_line.unit_price, product.list_price)
        sale_line.discount1 = Decimal('0.6')
        self.assertEqual(sale_line.unit_price, Decimal('2.8800'))
        self.assertEqual(sale.untaxed_amount, Decimal('2.8800'))

        # Modify Header
        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale.price_list = None
        sale_line = sale.lines.new()
        sale_line.product = product
        sale_line.quantity = 1.0
        self.assertEqual(sale_line.discount1, Decimal('0.0'))
        self.assertEqual(sale_line.discount2, Decimal('0.0'))
        self.assertEqual(sale_line.discount3, Decimal('0.0'))
        self.assertEqual(sale_line.unit_price, Decimal('10'))
        self.assertEqual(sale_line.amount, Decimal('10'))
        sale.save()
        modify_header = sale.click('modify_header')
        self.assertEqual(modify_header.form.party, customer)
        modify_header.form.price_list = price_list
        modify_header.execute('modify')
        sale_line, = sale.lines
        self.assertEqual(sale_line.amount, Decimal('3.6000'))
        self.assertEqual(sale_line.discount, Decimal('0.6400'))

        self.assertEqual(sale_line.discount1, Decimal('0.5'))

        self.assertEqual(sale_line.discount2, Decimal('0.2'))

        self.assertEqual(sale_line.discount3, Decimal('0.1'))
        self.assertEqual(sale.untaxed_amount, Decimal('3.60'))
