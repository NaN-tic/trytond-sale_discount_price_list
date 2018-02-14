# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.sale_discount_price_list.tests.test_sale_discount_price_list import suite
except ImportError:
    from .test_sale_discount_price_list import suite

__all__ = ['suite']
