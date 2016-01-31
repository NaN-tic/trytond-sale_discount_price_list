#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from .sale import *
from .price_list import *

def register():
    Pool.register(
        SaleLine,
        PriceList,
        PriceListLine,
        module='sale_discount_price_list', type_='model')

