# This file is part of sale_discount_price_list module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    @fields.depends('unit_price', 'product', 'quantity', 'unit',
        'discount1', 'discount2', 'discount3', 'sale', '_parent_sale.price_list')
    def update_discounts(self,):
        pool = Pool()
        PriceList = pool.get('product.price_list')
        Party = pool.get('party.party')

        price_list = None
        context = Transaction().context

        if self.sale and self.sale.price_list:
            price_list = self.sale.price_list
            party = self.sale.party
        elif context.get('price_list') and context.get('customer'):
            price_list = PriceList(context.get('price_list'))
            party = Party(context.get('customer'))
        if price_list and self.unit:
            discounts = price_list.compute_discount(
                party, self.product, self.unit_price,
                self.discount1 or 0, self.discount2 or 0, self.discount3 or 0,
                self.quantity or 0, self.unit)
            c = 1
            for discount in discounts:
                if discount is not None:
                    setattr(self, 'discount%d' % c, discount)
                c += 1

    @fields.depends('quantity')
    def on_change_product(self):
        if self.quantity is not None:
            self.update_discounts()
        super().on_change_product()

    @fields.depends('quantity')
    def on_change_quantity(self):
        if self.quantity is not None:
            self.update_discounts()
        super().on_change_quantity()
