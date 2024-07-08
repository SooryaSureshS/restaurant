import datetime

from odoo import api, models, fields,_
from collections import OrderedDict
from datetime import date, timedelta
from odoo.exceptions import ValidationError


class AccountingSummaryWizard(models.TransientModel):
    _name = 'accounting.summary.report'

    end_date = date.today().replace(day=1) - timedelta(days=1)
    print(end_date,"e")
    start_date = date.today().replace(day=1) - timedelta(days=end_date.day)
    print(start_date,"sss")

    def print_report(self):
        # today = date.today()
        # current_day = today.strftime("%d")
        # if current_day != '01':
        #     raise ValidationError(_('Please complete the monthly stocktake'))

        return self.env.ref('accounting_summary_report.report_accounting_summary').report_action(self)

    def get_date(self):
        date = self.start_date.strftime("%B-%Y")
        return date

    def net_sale(self):
        datas = self.env['sale.order'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('order_line.product_id.type', '!=', 'service'),
             ('order_line.product_id.list_price', '!=', 0)
             ])
        orders = datas.order_line.filtered(
            lambda line: line.product_id.type != 'service' and line.product_id.list_price != 0)

        data = orders.mapped('product_id').ids
        product = self.env['product.product'].browse(data)
        retail =0
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
        return retail
    def get_discount_details(self):

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

        discount_data = {'total_discount_paper': total_discount_paper, 'total_discount_food': total_discount_food}

        return discount_data

    def get_scrap_details(self):

        data = self.env['sale.order.line'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ]).mapped('product_id').ids

        product = self.env['product.product'].browse(data)

        product_dict = {}
        scrap_qty_details = {}
        for group in self.env['sale.order.line'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ],
                fields=['product_id', 'product_uom_qty'], groupby=['product_id']):

            p_id = group['product_id'][0]
            p_list = []
            total_price = 0
            qty = 0
            raw_waste = 0
            paper_waste = 0
            paper_qty = 0
            food_wastes=0
            paper_wastes = 0
            raw_qty_food = 0
            raw_qty_paper = 0
            for line in product:
                amount = line.qty_available * line.list_price
                p_list.append(amount)
                total_price = 0
                for price in p_list:
                    total_price += price




                scrap = self.env['stock.scrap'].search(
                    [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                     ('product_id', '=', line.id)])


                if scrap:
                    for prod in scrap:
                        if prod.product_id.category_type_id.name == 'Food':
                            scrap_quantity = prod.scrap_qty
                            qty += scrap_quantity
                            wastes = qty * prod.product_id.list_price
                            food_wastes = food_wastes + wastes

                    for prod in scrap:
                        if prod.product_id.category_type_id.name == 'Paper':
                            scrap_quantities = prod.scrap_qty
                            paper_qty += scrap_quantities
                            wastes = qty * prod.product_id.list_price
                            paper_wastes = paper_wastes + wastes


                if line.raw_material_ids:
                    for raw in line.raw_material_ids:
                        raw_scrap = self.env['stock.scrap'].search(
                            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                             ('product_id', '=', raw.product_id.id)])
                        print(raw_scrap,'e')
                        if raw_scrap:
                            for x in raw_scrap:
                                if x.product_id.category_type_id.name == 'Food':
                                    raw_qty = raw.product_qty *raw.product_id.list_price
                                    raw_qty_food = raw_qty_food +raw_qty
                                    print(raw_qty_food,"food")
                                elif x.product_id.category_type_id.name == 'Paper':
                                    raw_qty = raw.product_qty *raw.product_id.list_price
                                    raw_qty_paper = raw_qty_paper +raw_qty

            scrap_qty_details = {'finished_waste': food_wastes, 'raw_waste': raw_qty_food, "paper_finished": paper_wastes,
                                 'paper_raw': raw_qty_paper
                                 }
        return scrap_qty_details

    def get_stock_details(self):

        data = self.env['stock.move'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('location_id.id', '=', 8), ('location_dest_id.id', '=', 5)]).mapped('product_id').ids
        product = self.env['product.product'].browse(data)
        stock_details = {}
        for group in self.env['stock.move'].read_group(
                [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
                 ('location_id.id', '=', 8), ('location_dest_id.id', '=', 5)],
                fields=['product_id', 'product_uom_qty'], groupby=['product_id']):
            p_id = group['product_id'][0]
            food_openstock_qty = 0
            food_openstock = 0
            food_endstock_qty = 0
            food_endstock = 0
            paper_endstock_qty = 0
            paper_openstock = 0
            product_list = []
            paper_product_list = []

            for line in product:
                if line.category_type_id.name == 'Food':
                    if line.name not in product_list:
                        product_list.append(line.name)
                        food_virtual_available_start = line.with_context(to_date=self.start_date).virtual_available
                        price = food_virtual_available_start * line.list_price
                        food_openstock_qty = food_openstock_qty + price

                        food_qty_onhand = line.qty_available
                        end_stock_price = food_qty_onhand * line.list_price
                        food_endstock_qty = food_endstock_qty + end_stock_price

                    else:
                        pass
                if line.category_type_id.name == 'paper':
                    if line.name not in paper_product_list:
                        paper_product_list.append(line.name)
                        food_virtual_available_start = line.with_context(to_date=self.start_date).virtual_available
                        price = food_virtual_available_start * line.list_price
                        paper_openstock = paper_openstock + price
                        paper_qty_onhand = line.qty_available
                        end_stock_price = paper_qty_onhand * line.list_price
                        paper_endstock_qty = paper_endstock_qty + end_stock_price
                    else:
                        pass
            stock_details = {'food_openstock': food_openstock_qty, 'food_endstock': food_endstock_qty,
                             'paper_openstock': paper_openstock, 'paper_endstock': paper_endstock_qty,
                             }
            return stock_details

    def get_cost_details(self):

        food_purchase_data = self.env['purchase.order'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('order_line.product_id.category_type_id.name', '=', "Food")])
        paper_purchase_data = self.env['purchase.order'].sudo().search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date),
             ('order_line.product_id.category_type_id.name', '=', "Paper")])

        purchase_total = 0
        paper_purchase_total = 0
        for line in food_purchase_data:
            for x in line.order_line:
                single_product_pur = x.product_qty * x.price_unit
                purchase_total =purchase_total +single_product_pur



        for line in paper_purchase_data:
            for x in line.order_line:
                single_product = x.product_qty * x.price_unit
                paper_purchase_total =paper_purchase_total +single_product


        cost_details = {'food_purchase_total': purchase_total, 'paper_purchase_total': paper_purchase_total
                        }
        return cost_details

    def get_product_details(self):

        products = self.env['product.product'].search([])
        product_dict = {}
        stock = 0
        for prod in products:
            rec = prod.category_type_id.name
            end_qty = prod.with_context(to_date=self.end_date).qty_available


            if end_qty != 0:
                stock = end_qty * prod.list_price
                if rec in product_dict:
                    product_dict[rec].append({

                        'name': prod.name,
                        'stock': stock,

                    })
                else:
                    product_dict[rec] = [{

                        'name': prod.name,
                        'stock': stock,

                    }]
            else:
                pass
        return product_dict

    def promotion_details(self):
        total_reward_food = 0
        total_reward_paper = 0
        summary = self.env['sale.order'].search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)])
        for datas in summary:
            if datas.no_code_promo_program_ids:
                for x in datas.no_code_promo_program_ids:
                    if x.reward_product_id.category_type_id == 'Food':
                        total_reward_food = total_reward_food + x.discount_max_amount
                    if x.reward_product_id.category_type_id == 'Paper':
                        total_reward_paper = total_reward_paper + x.discount_max_amount


        promo_details={'total_reward_food': total_reward_food, 'total_reward_paper': total_reward_paper
                       }
        return promo_details

    def discount_details(self):

        total_discount_paper = 0
        discount_details = self.env['sale.order'].search(
            [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)])
        for datas in discount_details:
            if datas.order_line:
                for x in datas.order_line:
                    if x.discount:
                        if x.product_template_id.category_type_id == 'Paper':
                            total_discount_paper = total_discount_paper + x.price_total

        return total_discount_paper



        # # product = OrderedDict(sorted(product_dict.items()))
        # return product_dict
