# This file is part of sale_discount_price_list module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.config import config


__all__ = ['SaleLine']
__metaclass__ = PoolMeta


class SaleLine:
    __name__ = 'sale.line'

    @fields.depends('unit_price', 'discount', '_parent_sale.sale_discount_price_list',
        '_parent_sale.price_list')
    def on_change_product(self):
        res = super(SaleLine, self).on_change_product()
        if 'unit_price' in res:
            self.gross_unit_price = res['unit_price']
            self.discount = Decimal(0)
            res.update(self.update_prices())
        if 'discount' not in res:
            if hasattr(self, 'sale') and getattr(self.sale, 'price_list', None):
                discount = self.sale.price_list.compute_discount(
                    self.sale.party, self.product, self.unit_price,
                    self.discount, self.quantity, self.unit)
                if not discount is None:
                    res['discount'] = discount
            if self.discount is None:
                res['discount'] = Decimal(0)
        return res

    @fields.depends('unit_price', 'discount', '_parent_sale.sale_discount_price_list')
    def on_change_quantity(self):
        res = super(SaleLine, self).on_change_quantity()
        if 'unit_price' in res:
            self.gross_unit_price = res['unit_price']
            res.update(self.update_prices())
        if 'discount' not in res:
            if hasattr(self, 'sale') and getattr(self.sale, 'price_list', None):
                discount = self.sale.price_list.compute_discount(
                    self.sale.party, self.product, self.unit_price,
                    self.discount, self.quantity, self.unit)
                if not discount is None:
                    res['discount'] = discount
            if self.discount is None:
                res['discount'] = Decimal(0)
        return res
