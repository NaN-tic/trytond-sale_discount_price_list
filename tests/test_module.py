
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal
from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.modules.company.tests import (
    CompanyTestMixin, create_company, set_company)
from trytond.transaction import Transaction


class SaleDiscountPriceListTestCase(CompanyTestMixin, ModuleTestCase):
    'Test SaleDiscountPriceList module'
    module = 'sale_discount_price_list'

    @with_transaction()
    def test_product_price_list(self):
        'Test price_list'
        pool = Pool()
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        Uom = pool.get('product.uom')
        PriceList = pool.get('product.price_list')
        Category = pool.get('product.category')

        company = create_company()
        with set_company(company):
            kilogram, = Uom.search([
                    ('name', '=', 'Kilogram'),
                    ])
            gram, = Uom.search([
                    ('name', '=', 'Gram'),
                    ])

            account_category = Category(
                name='Account Category',
                accounting=True,
                )
            account_category.save()

            template = Template(
                name='product',
                list_price=Decimal(10),
                default_uom=kilogram,
                account_category=account_category,
                salable=True,
                sale_uom=kilogram,
                )
            template.save()
            variant1 = Product(template=template)
            variant1.save()
            variant2 = Product(template=template)
            variant2.save()
            variant3 = Product(template=template)
            variant3.save()
            variant4 = Product(template=template)
            variant4.save()

            price_list, = PriceList.create([{
                        'name': 'Default Price List',
                        'price': 'list_price',
                        'lines': [('create', [{
                                        'quantity': 10.0,
                                        'product': variant1.id,
                                        'formula': 'unit_price * 0.5',
                                        }, {
                                        'quantity': None,
                                        'product': variant1.id,
                                        'formula': 'unit_price * 0.8',
                                        }, {
                                        'quantity': None,
                                        'product': variant2.id,
                                        'formula': 'unit_price * 0.9',
                                        'discount_rate': Decimal('0.1'),
                                        }, {
                                        'quantity': None,
                                        'product': variant3.id,
                                        'base_price_formula': 'unit_price*Decimal(0.2)',
                                        'formula': '0',
                                        }, {
                                        'quantity': None,
                                        'product': variant4.id,
                                        'base_price_formula': 'unit_price*Decimal(0.2)',
                                        'formula': '0',
                                        'discount_rate': Decimal('0.1'),
                                        }, {
                                        'formula': 'unit_price',
                                        }])],
                        }])

            tests = [
                (variant1, Decimal('8.0000')),
                (variant2, Decimal('9.0000')),
                (variant3, Decimal('2.0000')),
                (variant4, Decimal('1.8000')),
                ]
            with Transaction().set_context(price_list=price_list.id):
                for product, unit_price in tests:
                    product = Product(product.id)
                    self.assertEqual(product.sale_price_uom, unit_price)

del ModuleTestCase
