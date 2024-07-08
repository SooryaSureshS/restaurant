from odoo import api, models, fields,_
from collections import OrderedDict
from odoo.exceptions import UserError, ValidationError



class EndingInventoryWizard(models.TransientModel):
    _name = 'ending.inventory.report'

    start_date = fields.Date('Start Date',required=True)
    end_date = fields.Date('End Date',required=True)

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('Start Date cannot be greater than  End Date'))

    def print_report(self):
        return self.env.ref('ending_inventory_report.report_ending_inventory').report_action(self)

    def get_date(self):
        date=self.start_date.strftime("%B-%Y")
        return date
    def total_amount(self):
        data = self.env['stock.move'].sudo().search([('create_date', '>=', self.start_date), ('create_date','<=',self.end_date),
                                                     ('location_id.id','=',8),('location_dest_id.id','=',5),('product_id.type','!=','consu')])

        for line in data:
            amount=sum(line.product_id.qty_available *line.product_id.list_price)

    def get_product_details(self):

        data = self.env['stock.move'].sudo().search([('create_date', '>=', self.start_date), ('create_date','<=',self.end_date),
                                                     ('product_id.type', '!=', 'service') ,('location_id.id','=',8),('location_dest_id.id','=',5)]).mapped('product_id').ids


        product = self.env['product.product'].browse(data)


        product_dict={}
        for group in self.env['stock.move'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service'),('location_id.id','=',8),('location_dest_id.id','=',5)
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit'], groupby=['product_id']):


            p_id = group['product_id'][0]

            for line in product:
                virtual_available_start = line.with_context(to_date=self.start_date).virtual_available
                if virtual_available_start > 0:
                    stock_per = group['product_uom_qty'] / virtual_available_start
                else:
                    stock_per= 0

                rec = line.category_type_id.name
                if line.id == p_id:
                    if rec in product_dict:
                        product_dict[rec].append({

                            'id': group['product_id'][0],
                            'qty': line.qty_available,
                            'name': line.name,
                            'carton': line.theoretical_carton,
                            'sleeve': line.theoretical_sleeve,
                            'uom': line.uom_id.name,
                            'unit_price': line.list_price,
                            'total_unit': group['product_uom_qty'],
                            'categ_type': line.category_type_id.name,
                            'standard_price': line.standard_price,
                            'stock_per':stock_per

                        })
                    else:
                        product_dict[rec] = [{
                                'id': group['product_id'][0],
                                'qty': line.qty_available,
                                'name': line.name,
                                'carton': line.theoretical_carton,
                                'sleeve': line.theoretical_sleeve,
                                'uom': line.uom_id.name,
                                'unit_price': line.list_price,
                                'total_unit': group['product_uom_qty'],
                                'categ_type': line.category_type_id.name,
                                'standard_price': line.standard_price,
                                'stock_per': stock_per

                        }]
        # product = OrderedDict(sorted(product_dict.items()))
        return product_dict








