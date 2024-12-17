# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal
from simpleeval import simple_eval

from trytond.model import fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval, Bool
from trytond.i18n import gettext
from trytond.tools import decistmt
from trytond.modules.product_price_list.price_list import FormulaError, Null


class PriceList(metaclass=PoolMeta):
    __name__ = 'product.price_list'

    def get_price_line(self, product, quantity, uom, pattern=None):
        Uom = Pool().get('product.uom')

        def parents(categories):
            for category in categories:
                while category:
                    yield category
                    category = category.parent

        if pattern is None:
            pattern = {}

        pattern = pattern.copy()
        if product:
            pattern['categories'] = [
                c.id for c in parents(product.categories_all)]
            pattern['product'] = product.id
        pattern['quantity'] = Uom.compute_qty(
            uom or self.get_uom(product), quantity, self.get_uom(product),
            round=False) if product else quantity

        for line in self.lines:
            if line.match(pattern):
                return line

    def compute_base_price(self, product, quantity, uom, pattern=None):
        line = self.get_price_line(product, quantity, uom, pattern=pattern)
        if line:
            context = self.get_context_formula(
                product, quantity, uom, pattern=pattern)
            unit_price = line.get_base_price(**context)
            if isinstance(unit_price, Null):
                unit_price = None
            return unit_price

    def compute_discount_rate(self, product, quantity, uom, pattern=None):
        line = self.get_price_line(product, quantity, uom, pattern=pattern)
        if line:
            return line.discount_rate


class PriceListLine(metaclass=PoolMeta):
    __name__ = 'product.price_list.line'

    base_price_formula = fields.Char('Base Price Formula',
        help=('Python expression that will be evaluated with:\n'
            '- unit_price: the original unit_price\n'
            '- cost_price: the cost price of the product\n'
            '- list_price: the list price of the product'))

    discount_rate = fields.Numeric("Discount Rate", digits=(16, 4))

    @classmethod
    def __setup__(cls):
        super().__setup__()
        readonly = ((Bool(Eval('base_price_formula', False)))
            & (Eval('discount_rate', None) != None))
        if cls.formula.states.get('readonly'):
            cls.formula.states['readonly'] |= readonly
        else:
            cls.formula.states['readonly'] = readonly

    @fields.depends('base_price_formula', 'discount_rate')
    def update_formula(self):
        if (self.base_price_formula
                and self.discount_rate is not None):
            self.formula = '0'

    @fields.depends('base_price_formula', 'discount_rate')
    def on_change_base_price_formula(self):
        self.update_formula()

    @fields.depends('base_price_formula', 'discount_rate')
    def on_change_discount_rate(self):
        self.update_formula()

    @classmethod
    def validate_fields(cls, lines, field_names):
        super().validate_fields(lines, field_names)
        cls.check_base_price_formula(lines, field_names)

    @classmethod
    def check_base_price_formula(cls, lines, field_names=None):
        if field_names and not (field_names & {'price_list', 'base_price_formula'}):
            return
        for line in lines:
            if line.base_price_formula is None or line.base_price_formula == '':
                continue

            context = line.price_list.get_context_formula(
                product=None, quantity=0, uom=None)
            try:
                if not isinstance(line.get_base_price(**context), Decimal):
                    raise ValueError
            except Exception as exception:
                raise FormulaError(
                    gettext('product_price_list.msg_invalid_formula',
                        formula=line.base_price_formula,
                        line=line.rec_name,
                        exception=exception)) from exception

    def get_base_price(self, **context):
        'Return base price (as Decimal)'
        context.setdefault('functions', {})['Decimal'] = Decimal
        if self.base_price_formula is None or self.base_price_formula == '':
            return
        return simple_eval(decistmt(self.base_price_formula), **context)
