# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.modules.product.product import round_price
from trytond.transaction import Transaction


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    @classmethod
    def get_sale_price_uom(cls, products, name):
        pool = Pool()
        PriceList = pool.get('product.price_list')

        prices = super().get_sale_price_uom(products, name)

        context = Transaction().context
        price_list_id = context.get('price_list')

        if price_list_id:
            price_list = PriceList(price_list_id)

            quantity = Transaction().context.get('quantity') or 0

            for product in products:
                line = price_list.get_price_line(product, quantity, product.default_uom)
                if line and line.formula == '0' and line.base_price_formula:
                    base_price = price_list.compute_base_price(
                        product, quantity, product.default_uom)
                    if base_price is not None:
                        unit_price = round_price(base_price)
                        prices[product.id] = unit_price

        return prices
