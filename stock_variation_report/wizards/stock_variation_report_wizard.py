from odoo import api, models, fields,_
from collections import OrderedDict
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError


class StockVariationWizard(models.TransientModel):
    _name = 'stock.variation.report'

    start_date = fields.Date('Start Date' ,required=True)
    end_date = fields.Date('End Date' ,required=True)

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('Start Date cannot be greater than  End Date'))

    def print_report(self):
        return self.env.ref('stock_variation_report.report_stock_variation').report_action(self)

    def get_date(self):
        date = self.start_date.strftime("%B-%Y")
        return date

    def get_product_details(self):

        data = self.env['stock.move'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('location_id.id', '=', 8), ('location_dest_id.id', '=', 5)]).mapped('product_id').ids
        product = self.env['product.product'].browse(data)
        products = product.filtered(
            lambda line: line.type != 'service'
        )
        product_dict = {}
        # product_transfer = self.env['stock.move'].sudo().search(
        #     [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
        #      ]).mapped('product_id').ids
        # product = self.env['product.product'].browse(product_transfer)

        for group in self.env['stock.move'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('location_id.id', '=', 8), ('location_dest_id.id', '=', 5),('product_id.type', '!=', 'service')],
                fields=['product_id', 'product_uom_qty'], groupby=['product_id']):

            p_id = group['product_id'][0]
            for line in products:

                last_day_of_prev_month = self.start_date - timedelta(days=1)
                open_stock = line.with_context(to_date=last_day_of_prev_month).virtual_available
                virtual_available_start = line.with_context(to_date=self.start_date).virtual_available
                rec = line.category_type_id.name
                qty =0

                if line.id == p_id:

                    datas = self.env['stock.move'].sudo().search(
                                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),('product_id.id', '=', line.id),
                                 ('location_id.id', '=', 8), ('location_dest_id.id', '!=', 5)])

                    for x in datas:
                        qty =qty+x.product_uom_qty
                    scrap_qty = 0
                    raw_waste = 0
                    for x in line.raw_material_ids:

                        scrap = self.env['stock.scrap'].search(
                            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                             ('product_id.id', '=', x.product_id.id)])
                        if scrap:
                            for prod in scrap:
                                scrap_quantity = prod.scrap_qty
                                scrap_qty += scrap_quantity
                        raw_waste = scrap_qty

                    credits = self.env['account.move'].search(
                            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                             ('invoice_line_ids.product_id.id', '=', line.id),
                             ('move_type', '=', 'in_refund')
                             ])
                    count = 0
                    if credits:
                        for x in credits:
                            count += 1
                    else:
                        count = 0
                    perc_diff = 0
                    if line.virtual_available >0:
                        product_diff = line.virtual_available - group['product_uom_qty']
                        perc_diff = (product_diff / line.virtual_available)*100
                    else:
                        perc_diff =0

                    purchase_order = self.env['stock.move'].sudo().search(
                            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                             ('product_id.id', '=', line.id),
                             ('location_dest_id.id', '=', 8)])
                    purchase = 0
                    if purchase_order:
                        for x in purchase_order:
                            purchase = x.product_uom_qty



                    if rec in product_dict:
                        product_dict[rec].append({

                                    'id': group['product_id'][0],
                                    'qty': group['product_uom_qty'],
                                    'name': line.name,
                                    'uom': line.uom_id.name,
                                    'unit_price': line.list_price,
                                    'end_stock': line.qty_available,
                                    'categ_type': line.category_type_id.name,
                                    'standard_price': line.standard_price,
                                    'stock_in': purchase,
                                    'open_stock': open_stock,
                                    'proj_usage': line.virtual_available,
                                    'transfers': qty,
                                    'credit': count,
                                    'raw_waste': raw_waste,
                                    'perc_diff': perc_diff,
                                    'virtual_available_start':virtual_available_start,

                                })
                    else:
                        product_dict[rec] = [{


                                    'id': group['product_id'][0],
                                    'qty': group['product_uom_qty'],
                                    'name': line.name,
                                    'uom': line.uom_id.name,
                                    'unit_price': line.list_price,
                                    'end_stock': line.qty_available,
                                    'categ_type': line.category_type_id.name,
                                    'standard_price': line.standard_price,
                                    'stock_in': purchase,
                                    'open_stock': open_stock,
                                    'proj_usage': line.virtual_available,
                                    'transfers': qty,
                                    'credit': count,
                                    'raw_waste': raw_waste,
                                    'perc_diff': perc_diff,
                                    'virtual_available_start':virtual_available_start,

                                }]

        # product = OrderedDict(sorted(product_dict.items()))
        return product_dict
