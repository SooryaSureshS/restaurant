from odoo import api, models, fields,_
from collections import OrderedDict
from odoo.exceptions import UserError, ValidationError


class QualityCostWizard(models.TransientModel):
    _name = 'quality.cost.report'

    start_date = fields.Date('Start Date' ,required=True)
    end_date = fields.Date('End Date' ,required=True)

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('Start Date cannot be greater than  End Date'))

    def print_report(self):
        return self.env.ref('quality_cost_report.report_quality_cost').report_action(self)

    def get_date(self):
        date = self.start_date.strftime("%B-%Y")
        return date

    def get_product_details(self):

        datas = self.env['sale.order'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('order_line.product_id.type', '!=', 'service'),
             ('order_line.product_id.list_price', '!=', 0)
             ])
        orders = datas.order_line.filtered(
            lambda line: line.product_id.type != 'service' and line.product_id.list_price != 0)

        data = orders.mapped('product_id').ids
        product = self.env['product.product'].browse(data)
        product_dict = {}
        retail =0
        total_diff_food =0
        total_diff_paper =0
        total_price_diff_food =0
        total_price_diff_paper =0
        for group in self.env['sale.order.line'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service'), ('price_unit', '!=', 0)
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
                 ('product_id.type', '!=', 'service'), ('price_unit', '!=', 0)
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit','discount','price_total'], groupby=['product_id']):
            p_id = group['product_id'][0]


            for line in product:

                if line.id == p_id:
                    purchase_order = self.env['purchase.order'].search(
                        [('order_line.product_id', '=', line.id), ('state', '=', 'purchase')
                         ], limit=1)

                    food_effective = 0
                    if purchase_order:
                        for x in purchase_order:
                            if x.effective_date:
                                effective_date = x.effective_date
                                food_effective = effective_date.strftime("%d-%b-%y")
                            else:
                                food_effective = 0
                    else:
                        food_effective = 0
                    item_effective = 0
                    domain = ['|',
                          '&', ('product_tmpl_id', '=', line.product_tmpl_id.id), ('applied_on', '=', '1_product'),
                          '&', ('product_id', '=', line.id), ('applied_on', '=', '0_product_variant')]

                    price = self.env['product.pricelist.item'].search(domain, limit=1)
                    if price:
                        for x in price:
                            if x.date_start:
                                item_effective_date = x.date_start
                                item_effective = item_effective_date.strftime("%d-%b-%y")
                            else:
                                item_effective = 0
                    else:
                        item_effective = 0
                    rec = line.name
                    if line.list_price >0:
                        food_cost_percentage =line.standard_price /line.list_price
                    else:
                        food_cost_percentage =0
                    total_paper_cost =0
                    paper_cost_per =0

                    for raw in line.raw_material_ids:
                        if raw.product_id.category_type_id.name =='Paper':
                            paper_cost = raw.product_id.standard_price
                            total_paper_cost =total_paper_cost+paper_cost
                            if raw.product_id.list_price >0:
                                paper_cost_per = raw.product_id.standard_price /raw.product_id.list_price
                            else:
                                paper_cost_per =0


                    scrap = self.env['stock.scrap'].search(
                        [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                         ('product_id.id', '=', line.id)])
                    made = 0
                    scrap_quantity =0
                    if scrap:
                        for prod in scrap:
                            scrap_quantity += prod.scrap_qty
                    else:
                        scrap_quantity =0

                    sold_qty = group['product_uom_qty']
                    made = sold_qty + scrap_quantity

                    food_cost_product = made * line.standard_price
                    sold_cost_food = sold_qty * line.standard_price

                    paper_cost_product=0
                    sold_cost_paper =0
                    for raw in line.raw_material_ids:
                        if raw.product_id.category_type_id.name =='Paper':
                            paper_cost_product = made *raw.product_id.standard_price
                            sold_cost_paper = made *raw.product_id.standard_price
                    if line.category_type_id.name =='Food':

                        sold_qty = group['product_uom_qty']
                        start_qty = line.with_context(to_date=self.start_date).virtual_available
                        actual_available_qty= start_qty -sold_qty
                        actual_available_qty_price= actual_available_qty *line.list_price
                        current_qty =line.qty_available
                        current_qty_price =current_qty*line.list_price
                        diff =current_qty - actual_available_qty
                        price_diff_food=current_qty_price-actual_available_qty_price
                        total_price_diff_food=total_price_diff_food+price_diff_food
                        total_diff_food =total_diff_food +diff


                    if line.category_type_id.name =='Paper':

                        sold_qty = group['product_uom_qty']
                        start_qty = line.with_context(to_date=self.start_date).virtual_available
                        actual_available_qty= start_qty -sold_qty
                        actual_available_qty_price= actual_available_qty *line.list_price
                        current_qty =line.qty_available
                        current_qty_price =current_qty*line.list_price
                        differ =current_qty - actual_available_qty
                        price_diff_paper=current_qty_price-actual_available_qty_price
                        total_price_diff_paper=total_price_diff_paper+price_diff_paper
                        total_diff_paper =total_diff_paper +differ



                    food_difference =total_price_diff_food /retail
                    paper_difference =total_price_diff_paper /retail





                    if rec in product_dict:
                        product_dict[rec].append({
                            'id': group['product_id'][0],
                            'qty': group['product_uom_qty'],
                            'name': line.name,
                            'uom': line.uom_id.name,
                            'unit_price': line.list_price,
                            'total_unit': line.qty_available,
                            'categ_type': line.category_type_id.name,
                            'food_cost_percentage': food_cost_percentage,
                            'food_cost': line.standard_price,
                            'effective_date': food_effective,
                            'item_date': item_effective,
                            'paper_cost': total_paper_cost,
                            'paper_cost_per': paper_cost_per,
                            'made': made,
                            'waste': scrap_quantity,
                            'food_cost_product': food_cost_product,
                            'paper_cost_product':paper_cost_product,
                            'retail':retail,
                            'sold_qty':sold_qty,
                            'sold_cost_food':sold_cost_food,
                            'sold_cost_paper':sold_cost_paper,
                            'food_difference':food_difference,
                            'paper_difference':paper_difference,
                            'total_price_diff_food':total_price_diff_food,
                            'total_price_diff_paper':total_price_diff_paper



                        })
                    else:
                        product_dict[rec] = [{
                            'id': group['product_id'][0],
                            'qty': group['product_uom_qty'],
                            'name': line.name,
                            'uom': line.uom_id.name,
                            'unit_price': line.list_price,
                            'total_unit': line.qty_available,
                            'categ_type': line.category_type_id.name,
                            'food_cost_percentage': food_cost_percentage,
                            'food_cost': line.standard_price,
                            'effective_date': food_effective,
                            'item_date': item_effective,
                            'paper_cost': total_paper_cost,
                            'paper_cost_per': paper_cost_per,
                            'made': made,
                            'waste': scrap_quantity,
                            'food_cost_product': food_cost_product,
                            'paper_cost_product':paper_cost_product,
                            'retail':retail,
                            'sold_qty':sold_qty,
                            'sold_cost_food':sold_cost_food,
                            'sold_cost_paper':sold_cost_paper,
                            'food_difference':food_difference,
                            'paper_difference':paper_difference,
                            'total_price_diff_food':total_price_diff_food,
                            'total_price_diff_paper':total_price_diff_paper



                        }]

        # res= OrderedDict(sorted(product_dict.items() ))
        return product_dict

    def zero_selling_price(self):

        datas = self.env['sale.order'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('order_line.product_id.type', '!=', 'service'),
             ('order_line.product_id.list_price', '=', 0)
             ])
        orders = datas.order_line.filtered(
            lambda line: line.product_id.type != 'service' and line.product_id.list_price == 0)

        data = orders.mapped('product_id').ids
        product = self.env['product.product'].browse(data)
        zero_product_dict={}


        for group in self.env['sale.order.line'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service'), ('price_unit', '=', 0)
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit','price_total'], groupby=['product_id']):
            p_id = group['product_id'][0]


            for line in product:

                if line.id == p_id:
                    purchase_order = self.env['purchase.order'].search(
                        [('order_line.product_id', '=', line.id), ('state', '=', 'purchase')
                         ], limit=1)

                    food_effective = 0
                    if purchase_order:
                        for x in purchase_order:
                            if x.effective_date:
                                effective_date = x.effective_date
                                food_effective = effective_date.strftime("%d-%b-%y")
                            else:
                                food_effective = 0
                    else:
                        food_effective = 0
                    item_effective = 0
                    domain = ['|',
                              '&', ('product_tmpl_id', '=', line.product_tmpl_id.id), ('applied_on', '=', '1_product'),
                              '&', ('product_id', '=', line.id), ('applied_on', '=', '0_product_variant')]

                    price = self.env['product.pricelist.item'].search(domain, limit=1)
                    if price:
                        for x in price:
                            if x.date_start:
                                item_effective_date = x.date_start
                                item_effective = item_effective_date.strftime("%d-%b-%y")
                            else:
                                item_effective = 0
                    else:
                        item_effective = 0
                    rec = line.name
                    if line.list_price >0:
                        food_cost_percentage =line.standard_price /line.list_price
                    else:
                        food_cost_percentage =0
                    total_paper_cost =0
                    paper_cost_per =0

                    for raw in line.raw_material_ids:
                        if raw.product_id.category_type_id.name =='Paper':
                            paper_cost = raw.product_id.standard_price
                            total_paper_cost =total_paper_cost+paper_cost
                            if raw.product_id.list_price >0:
                                paper_cost_per = raw.product_id.standard_price /raw.product_id.list_price
                            else:
                                paper_cost_per =0


                    scrap = self.env['stock.scrap'].search(
                        [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                         ('product_id.id', '=', line.id)])
                    made = 0
                    scrap_quantity =0
                    if scrap:
                        for prod in scrap:
                            scrap_quantity += prod.scrap_qty
                    else:
                        scrap_quantity =0

                    sold_qty = group['product_uom_qty']
                    made = sold_qty + scrap_quantity

                    food_cost_product = made * line.standard_price
                    sold_cost_food = sold_qty * line.standard_price
                    paper_cost_product=0
                    sold_cost_paper=0
                    for raw in line.raw_material_ids:
                        if raw.product_id.category_type_id.name =='Paper':
                            paper_cost_product = made *raw.product_id.standard_price
                            sold_cost_paper = made *raw.product_id.standard_price






                    if rec in zero_product_dict:
                        zero_product_dict[rec].append({
                            'id': group['product_id'][0],
                            'qty': group['product_uom_qty'],
                            'name': line.name,
                            'uom': line.uom_id.name,
                            'unit_price': line.list_price,
                            'total_unit': line.qty_available,
                            'categ_type': line.category_type_id.name,
                            'food_cost_percentage': food_cost_percentage,
                            'food_cost': line.standard_price,
                            'effective_date': food_effective,
                            'item_date': item_effective,
                            'paper_cost': total_paper_cost,
                            'paper_cost_per': paper_cost_per,
                            'made': made,
                            'waste': scrap_quantity,
                            'food_cost_product': food_cost_product,
                            'paper_cost_product':paper_cost_product,
                            'sold_qty':sold_qty,
                            'sold_cost_food':sold_cost_food,
                            'sold_cost_paper':sold_cost_paper,



                        })
                    else:
                        zero_product_dict[rec] = [{
                            'id': group['product_id'][0],
                            'qty': group['product_uom_qty'],
                            'name': line.name,
                            'uom': line.uom_id.name,
                            'unit_price': line.list_price,
                            'total_unit': line.qty_available,
                            'categ_type': line.category_type_id.name,
                            'food_cost_percentage': food_cost_percentage,
                            'food_cost': line.standard_price,
                            'effective_date': food_effective,
                            'item_date': item_effective,
                            'paper_cost': total_paper_cost,
                            'paper_cost_per': paper_cost_per,
                            'made': made,
                            'waste': scrap_quantity,
                            'food_cost_product': food_cost_product,
                            'paper_cost_product':paper_cost_product,
                            'sold_qty':sold_qty,
                            'sold_cost_food':sold_cost_food,
                            'sold_cost_paper':sold_cost_paper,



                        }]

        # res= OrderedDict(sorted(product_dict.items() ))
        return zero_product_dict

    def sundry_details(self):


        product = self.env['product.product'].search([('category_type_id.name', '=', 'Sundry'),('type', '!=', 'service')])

        total_used_food =0
        total_used_paper =0
        for line in product:


            if line.category_type_id.name =='Food':
                virtual_available_start = line.product_id.with_context(to_date=self.start_date).virtual_available
                virtual_available_end = line.product_id.with_context(to_date=self.end_date).virtual_available
                scrap_quantity =0
                scrap = self.env['stock.scrap'].search(
                    [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                     ('product_id.id', '=', line.id)])
                if scrap:
                    for prod in scrap:
                        scrap_quantity += prod.scrap_qty
                else:
                    scrap_quantity =0
                qty=virtual_available_start-virtual_available_end
                used_qty = qty -scrap_quantity
                used_qty_price = used_qty * line.list_price
                total_used_food = total_used_food +used_qty_price

            if line.category_type_id.name =='Paper':
                virtual_available_start = line.product_id.with_context(to_date=self.start_date).virtual_available
                virtual_available_end = line.product_id.with_context(to_date=self.end_date).virtual_available
                scrap_quantity =0
                scrap = self.env['stock.scrap'].search(
                    [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                     ('product_id.id', '=', line.id)])
                if scrap:
                    for prod in scrap:
                        scrap_quantity += prod.scrap_qty
                else:
                    scrap_quantity =0
                qty=virtual_available_start-virtual_available_end
                used_qty = qty -scrap_quantity
                used_qty_price = used_qty * line.list_price
                total_used_paper = total_used_paper +used_qty_price





        sundry_detail={'total_used_food': total_used_food, 'total_used_paper': total_used_paper
                         }
        return sundry_detail

    def complete_waste_details(self):

        total_scrap_food = 0
        total_scrap_paper = 0


        datas = self.env['sale.order'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)
             ])

        orders = datas.order_line.filtered(
        lambda line: line.product_id.type != 'service')


        data = orders.mapped('product_id').ids
        product = self.env['product.product'].browse(data)


        for line in product:


            if line.category_type_id.name == 'Food':


                scrap = 0
                scrap_details = self.env['stock.scrap'].search(
                    [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                     ('product_id.id', '=', line.id)])

                if scrap_details:
                    for prod in scrap_details:
                        scrap += prod.scrap_qty
                else:
                    scrap = 0

                scrap_price = scrap * line.standard_price
                total_scrap_food = total_scrap_food + scrap_price


            elif line.category_type_id.name == 'Paper':



                scrap = 0
                scrap_details = self.env['stock.scrap'].search(
                    [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                     ('product_id.id', '=', line.id)])

                if scrap_details:
                    for prod in scrap_details:
                        scrap += prod.scrap_qty
                else:
                    scrap = 0

                scrap_price = scrap * line.standard_price
                total_scrap_paper = total_scrap_paper + scrap_price


        complete_waste_detail={'total_scrap_food': total_scrap_food, 'total_scrap_paper': total_scrap_paper
                           }
        return complete_waste_detail

    def discount_details(self):

        total_discount_paper = 0
        total_discount_food = 0
        discount_details = self.env['sale.order'].search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),('order_line.product_template_id.type', '!=', 'service')])
        for datas in discount_details:
            if datas.order_line:
                for x in datas.order_line:
                    if x.discount:


                        if x.product_template_id.category_type_id.name == 'Paper':
                            if x.price_total == 0:
                                price_paper=x.price_unit*x.product_uom_qty
                                total_discount_paper = total_discount_paper +price_paper
                        if x.product_template_id.category_type_id.name == 'Food':
                            print(x.product_template_id.name)
                            print(x.price_unit*x.product_uom_qty,"jjj")

                            price_food=x.price_unit*x.product_uom_qty
                            total_discount_food = total_discount_food +price_food
                            print(total_discount_food,"dis")


        discount_detail={'total_dis_food': total_discount_food, 'total_dis_paper': total_discount_paper
                         }
        return discount_detail

    def get_retail_details(self):

        retail_price =0
        food_sale =0
        paper_sale =0

        datas = self.env['sale.order'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('order_line.product_id.type', '!=', 'service'),
             ('no_code_promo_program_ids', '=', False),('applied_coupon_ids', '=', False)
             ])
        print(datas,"dattat")
        orders = datas.order_line.filtered(
            lambda line: line.product_id.type != 'service' and line.discount == 0)
        print(orders,"ord")
        data = orders.mapped('product_id').ids
        product = self.env['product.product'].browse(data)

        for group in self.env['sale.order.line'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service'), ('discount', '=', '0')
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit','discount','price_total'], groupby=['product_id']):
            p_id = group['product_id'][0]

            for line in product:
                if line.id == p_id:
                    sold = group['product_uom_qty']
                    price_prod=line.list_price * sold
                    retail_price =retail_price + price_prod
                    print(retail_price,"rrr")

                    if line.category_type_id.name == 'Food':
                        sale_price_food = group['product_uom_qty'] * line.list_price
                        food_sale=food_sale+sale_price_food
                    if line.category_type_id.name == 'Paper':
                        sale_price_paper = group['product_uom_qty'] * line.list_price
                        paper_sale=paper_sale+sale_price_paper

        retail_detail={'retail_price': retail_price, 'food_sale':food_sale, 'paper_sale':paper_sale
                         }
        return retail_detail

    def get_discount_meal(self):

        dis_retail_price =0
        dis_food_sale =0
        dis_paper_sale =0

        datas = self.env['sale.order'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('order_line.product_id.type', '!=', 'service'),
             ])
        print(datas,"dattat")
        orders = datas.order_line.filtered(
            lambda line: line.product_id.type != 'service' and line.discount != 0)
        print(orders,"ord")
        data = orders.mapped('product_id').ids
        product = self.env['product.product'].browse(data)

        for group in self.env['sale.order.line'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('product_id.type', '!=', 'service'), ('discount', '!=', '0')
                 ],
                fields=['product_id', 'product_uom_qty', 'price_unit','discount','price_total'], groupby=['product_id']):
            p_id = group['product_id'][0]

            for line in product:
                if line.id == p_id:
                    sold = group['product_uom_qty']
                    price_prod=line.list_price * sold
                    dis_retail_price =dis_retail_price + price_prod
                    print(dis_retail_price,"rrr")

                    if line.category_type_id.name == 'Food':
                        sale_price_food = group['product_uom_qty'] * line.list_price
                        dis_food_sale=dis_food_sale+sale_price_food
                    if line.category_type_id.name == 'Paper':
                        sale_price_paper = group['product_uom_qty'] * line.list_price
                        dis_paper_sale=dis_paper_sale+sale_price_paper

        dis_retail_detail={'dis_retail_price': dis_retail_price, 'dis_food_sale':dis_food_sale, 'dis_paper_sale':dis_paper_sale
                       }
        return dis_retail_detail

