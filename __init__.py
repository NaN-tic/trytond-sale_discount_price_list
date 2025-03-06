# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import sale
from . import price_list
from . import product

def register():
    Pool.register(
        sale.SaleLine,
        price_list.PriceList,
        price_list.PriceListLine,
        product.Product,
        module='sale_discount_price_list', type_='model')
