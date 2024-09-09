# This file is part of sale_discount_price_list module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction
from trytond.modules.product import round_price


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    @fields.depends('product', 'quantity', 'unit', 'sale',
        '_parent_sale.price_list')
    def update_discount(self,):
        pool = Pool()
        PriceList = pool.get('product.price_list')

        price_list = None
        context = Transaction().context

        if self.sale:
            price_list = self.sale.price_list
        if context.get('price_list'):
            price_list = PriceList(context.get('price_list'))
        if price_list and self.unit:
            discount_rate = price_list.compute_discount_rate(self.product,
                self.quantity, self.unit)
            if not discount_rate is None:
                self.discount_rate = discount_rate
                self.on_change_discount_rate()

    @fields.depends('product', 'unit')
    def compute_base_price(self):
        pool = Pool()
        Tax = pool.get('account.tax')
        Date = pool.get('ir.date')

        res = super().compute_base_price()

        today = Date.today()
        price_list = (self.sale.price_list
            if self.sale and self.sale.price_list else None)
        if self.product and price_list:
            price = price_list.compute_base_price(self.product,
                self.quantity, self.unit)
            if price_list.tax_included and self.taxes and price is not None:
                price = Tax.reverse_compute(price, self.taxes, today)
            if not price is None:
                return round_price(price)
        return res

    @fields.depends('quantity')
    def on_change_product(self):
        super().on_change_product()
        self.update_discount()

    @fields.depends('quantity')
    def on_change_quantity(self):
        super().on_change_quantity()
        self.update_discount()
