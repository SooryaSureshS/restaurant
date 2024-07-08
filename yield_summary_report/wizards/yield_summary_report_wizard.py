from odoo import api, models, fields,_
from collections import OrderedDict
from odoo.exceptions import UserError, ValidationError


class YieldSummaryWizard(models.TransientModel):
    _name = 'yield.summary'

    start_date = fields.Date('Start Date' ,required=True)
    end_date = fields.Date('End Date' ,required=True)

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('Start Date cannot be greater than  End Date'))

    def print_report(self):

        return self.env.ref('yield_summary_report.report_yield_summary').report_action(self)

    def get_date(self):
        date = self.start_date.strftime("%B-%Y")
        return date

    def get_product_details(self):

        data = self.env['stock.move'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),('product_id.type', '!=', 'service'),('location_id.id','=',8),('location_dest_id.id','=',5)
             ]).mapped('product_id').ids
        print(data,"daa")
        product = self.env['product.product'].browse(data)

        product_dict = {}
        sold =0
        retail =0
        for group in self.env['stock.move'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service'),('location_id.id','=',8),('location_dest_id.id','=',5)
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit'], groupby=['product_id']):


            p_id = group['product_id'][0]
            for lines in product:
                if lines.id == p_id:

                    for line in lines.raw_material_ids:
                        sold=0
                        print(lines.name)
                        print(line.product_id.name)
                        sold = sold +line.product_qty
                        print(sold)
                        price_prod=(line.unit_price * sold)*group['product_uom_qty']
                        print(group['product_uom_qty'],"kkk")
                        print(price_prod,"rr")
                        retail =retail + price_prod
            print(retail,"re")
        for group in self.env['stock.move'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service'),('location_id.id','=',8),('location_dest_id.id','=',5)
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit'], groupby=['product_id']):


            p_id = group['product_id'][0]

            for lines in product:
                if lines.id == p_id:


                    if lines.raw_material_ids:

                        for line in lines.raw_material_ids:

                            qty_sales = (line.unit_price*line.product_qty)*group['product_uom_qty']
                            total_units = line.product_id.qty_available*line.product_id.list_price



                            virtual_available_start = line.product_id.with_context(to_date=self.start_date).virtual_available
                            virtual_available_end = line.product_id.with_context(to_date=self.end_date).virtual_available




                            product_per =(( (line.unit_price*line.product_qty)*group['product_uom_qty'])/retail)*100


                            rec = product_per
                            if line.id:
                                if rec in product_dict:
                                    product_dict[rec].append({


                            'qty': qty_sales,
                            'name': line.product_id.name,
                            'uom': line.uom_id.name,
                            'unit_price': line.unit_price,
                            'total_unit': total_units,
                            'categ_type': line.product_id.category_type_id.name,
                            'standard_price': line.product_id.standard_price,
                            'product_per': product_per,
                            'virtual_available_start': virtual_available_start,
                        })

                                else:
                                   product_dict[rec] = [{

                            'qty': qty_sales,
                            'name': line.product_id.name,
                            'uom': line.uom_id.name,
                            'unit_price': line.unit_price,
                            'total_unit': total_units,
                            'categ_type': line.product_id.category_type_id.name,
                            'standard_price': line.product_id.standard_price,
                            'product_per': product_per,
                            'virtual_available_start': virtual_available_start,
                        }]

        res = OrderedDict(sorted(product_dict.items(), reverse=True))

        return res
