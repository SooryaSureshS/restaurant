from odoo import api, models, fields


class ProductWizard(models.TransientModel):
    _name = 'promotion.coupon.report'

    start_date = fields.Date('Start Date',required=True)
    end_date = fields.Date('End Date',required=True)

    def print_report(self):


        return self.env.ref('promotion_and_coupon_program_report.report_promotion_and_coupon_program').report_action(self)


    @api.model
    def _get_report_values(self, docids, data=None):

        data_ids = self.env['sale.order'].sudo().search([]).mapped('order_line').mapped('product_id').ids
        data = self.env['product.product'].browse(data_ids)
        return {
            'doc': data,

        }


    def get_product_details(self):

        data = self.env['sale.order.line'].sudo().search([('create_date', '>=', self.start_date), ('create_date','<=',self.end_date),
                                                     ('product_id.type', '!=', 'service')])


        data = data.mapped('product_id').ids
        product = self.env['product.product'].browse(data)
        print(product,'ppp')


        product_dict={}
        total_food_costs =0
        total_paper_costs =0
        retail =0

        for group in self.env['sale.order.line'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service')
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit','discount','price_total'], groupby=['product_id']):
            p_id = group['product_id'][0]

            for line in product:
                if line.id == p_id:
                    sold = group['product_uom_qty']
                    price_prod=line.list_price * sold
                    retail =retail + price_prod
        for group in self.env['sale.order.line'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service')
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit'], groupby=['product_id']):
            print("product_uom_qty",group)


            p_id = group['product_id'][0]

            for line in product:
                virtual_available_start = line.with_context(to_date=self.start_date).virtual_available
                if virtual_available_start > 0:
                    stock_per = group['product_uom_qty'] / virtual_available_start
                else:
                    stock_per= 0

                rec = line.category_type_id.name
                food_cost_value =0
                if line.id == p_id:
                    if line.category_type_id.name == 'Food':
                        food_costs=group['product_uom_qty']*line.list_price
                        total_food_costs =total_food_costs +food_costs
                    if line.category_type_id.name == 'Paper':
                        paper_costs=group['product_uom_qty']*line.list_price
                        total_paper_costs =total_paper_costs +paper_costs



                    food_cost_value =group['product_uom_qty']*line.standard_price

                    print(total_food_costs,"pppp")

                    if rec in product_dict:
                        product_dict[rec].append({

                            'id': group['product_id'][0],
                            'name': line.name,
                            'qty': group['product_uom_qty'],
                            'categ_type': line.category_type_id.name,
                            'standard_price': line.standard_price,
                            'list_price': line.list_price,
                            'food_cost_value': food_cost_value,
                            'total_food_costs':total_food_costs,
                            'total_paper_costs':total_paper_costs,
                            'retail':retail,


                        })
                    else:
                        product_dict[rec] = [{
                            'id': group['product_id'][0],
                            'name': line.name,
                            'qty': group['product_uom_qty'],
                            'categ_type': line.category_type_id.name,
                            'standard_price': line.standard_price,
                            'list_price': line.list_price,
                            'food_cost_value': food_cost_value,
                            'total_food_costs':total_food_costs,
                            'total_paper_costs':total_paper_costs,
                            'retail':retail,

                        }]
        # product = OrderedDict(sorted(product_dict.items()))
        return product_dict
