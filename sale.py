# This file is part of sale_discount_price_list module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import PoolMeta


__all__ = ['SaleLine']


class SaleLine:
    __metaclass__ = PoolMeta
    __name__ = 'sale.line'

    @classmethod
    def __setup__(cls):
        super(SaleLine, cls).__setup__()
        cls.product.on_change.add('unit_price')
        cls.quantity.on_change.add('unit_price')

    def update_discounts(self,):
        if not getattr(self, 'discount1', False):
            if hasattr(self, 'sale') and hasattr(self.sale, 'price_list') \
                    and self.sale.price_list:
                discounts = self.sale.price_list.compute_discount(
                    self.sale.party, self.product, self.unit_price,
                    self.discount1, self.discount2, self.discount3,
                    self.quantity or 0, self.unit)
                c = 1
                for discount in discounts:
                    setattr(self, 'discount%d' % c, discount)
                    c += 1

    def on_change_product(self):
        super(SaleLine, self).on_change_product()
        self.update_discounts()

    def on_change_quantity(self):
        super(SaleLine, self).on_change_quantity()
        self.update_discounts()
