from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleSeason(models.Model):
    _name = 'sale.season'
    _rec_name = 'name'

    name = fields.Char(required=True)
    start_date = fields.Date(copy=False, store=True)
    end_date = fields.Date(copy=False, store=True)
    products = fields.Many2many('product.product')
    state = fields.Selection([('draft', 'Draft'), ('ready', 'Ready'), ('purchased', 'Purchased'),
                              ('delivered', 'Delivered')], default='draft')

    def calculate_period(self, objs, start_date, end_date):
        if start_date and end_date:
            for rec in objs:
                if rec.start_date and rec.end_date:
                    if rec.start_date < start_date < rec.end_date:
                        return True
                    elif rec.start_date < end_date < rec.end_date:
                        return True
                    elif start_date < rec.start_date and end_date > rec.end_date:
                        return True
                    elif start_date == rec.start_date or end_date == rec.end_date:
                        return True
        return False

    @api.onchange('start_date', 'end_date')
    def onchange_date(self):
        for rec in self:
            if rec.state == 'draft':
                objs = self.search([('id', '!=', rec._origin.id)])
                if rec.start_date and rec.end_date:
                    if rec.start_date > rec.end_date:
                        raise ValidationError(_('Start date should be lesser than end date.'))
                    conflict = self.calculate_period(objs, rec.start_date, rec.end_date)
                    if conflict:
                        raise ValidationError(_('There are already seasons in this time period.'))

    def get_brand_orders(self, orders):
        brand_orders = dict()
        for order in orders:
            for line in order.order_line:
                brand = line.product_id.product_brand_id
                if brand:
                    if brand.id not in brand_orders:
                        brand_orders[brand.id] = []
                    brand_orders[brand.id].append(line)
                else:
                    if 'no_brand' not in brand_orders:
                        brand_orders['no_brand'] = []
                    brand_orders['no_brand'].append(line)
        return brand_orders

    def create_brand_po(self, brand_orders):
        for brand in brand_orders:
            brand_ob = self.env['product.brand'].browse(int(brand))
            po = self.env['purchase.order'].create({'partner_id': brand_ob.brand_vendor.id})
            products = dict()
            for line in brand_orders[brand]:
                if line.product_id.id not in products:
                    products[line.product_id.id] = {'product': line.product_id, 'qty': line.product_uom_qty,
                                                    'price': line.product_id.standard_price}
                else:
                    products[line.product_id.id]['qty'] += line.product_uom_qty
            for product in products:
                self.env['purchase.order.line'].create({'order_id': po.id, 'product_id': product,
                                                        'product_qty': products[product]['qty'],
                                                        'price_unit': products[product]['price']})

    def create_po(self):
        orders = self.env['sale.order'].search([('state', 'in', ['sale', 'done']),
                                                ('date_order', '>=', self.start_date),
                                                ('date_order', '<=', self.end_date)])
        brand_orders = self.get_brand_orders(orders)
        self.create_brand_po(brand_orders)
        self.state = 'purchased'
        return True

    def season_job(self):
        recs = self.search([('end_date', '=', datetime.today().date()), ('state', '=', 'ready')])
        for rec in recs:
            try:
                rec.create_po()
            except Exception as e:
                pass

    def create_do(self):
        # orders = self.env['sale.order'].search([('state', 'in', ['sale', 'done']),
        #                                         ('date_order', '>=', self.start_date),
        #                                         ('date_order', '<=', self.end_date)])
        # brand_orders = self.get_brand_orders(orders)
        # self.create_brand_po(brand_orders)
        # self.state = 'purchased'
        return True

    def ready(self):
        self.state = 'ready'
        return True

