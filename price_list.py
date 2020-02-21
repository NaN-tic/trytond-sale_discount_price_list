# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta, Pool
from trytond.modules.product import price_digits
from decimal import Decimal

__all__ = ['PriceList', 'PriceListLine']

ZERO_ = Decimal(0)


class PriceList:
    __name__ = 'product.price_list'
    __metaclass__ = PoolMeta

    def compute_discount(self, party, product, unit_price, discount1,
            discount2, discount3, quantity, uom, pattern=None):
        pool = Pool()
        Uom = pool.get('product.uom')
        PriceListLine = pool.get('product.price_list.line')

        if pattern is None:
            pattern = {}

        pattern = pattern.copy()
        pattern['product'] = product and product.id or None
        pattern['quantity'] = Uom.compute_qty(uom, quantity,
            product.default_uom, round=False) if product else quantity

        lines = PriceListLine.search([
                ('price_list', '=', self.id),
                ['OR',
                    ('product', '=', None),
                    ('product', '=', product and product.id or None),
                    ]
                ])
        for line in lines:
            if line.match(pattern):
                return (line.discount1 or ZERO_, line.discount2 or ZERO_,
                    line.discount3 or ZERO_)

        return discount1, discount2, discount3


class PriceListLine:
    __name__ = 'product.price_list.line'
    __metaclass__ = PoolMeta
    discount1 = fields.Numeric('Discount 1', digits=price_digits)
    discount2 = fields.Numeric('Discount 2', digits=price_digits)
    discount3 = fields.Numeric('Discount 3', digits=price_digits)
