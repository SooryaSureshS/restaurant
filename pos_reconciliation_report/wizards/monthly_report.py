# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import numpy as np

class AccountMonthlyReport(models.TransientModel):
    _name = "pos.monthly.report"
    _description = "POS Summary "

    offer_type = fields.Selection([('all', 'All'),
                                   ('coupon_promotion', 'Coupons Promotion Program'),
                                   ('loyalty', 'Loyalty Program'),
                                   ('discount', 'Discount applied')], string="Type")
    start_date = fields.Date(required=True, )
    end_date = fields.Date(required=True, )
    user_id = fields.Many2one('res.users', string='Login User',
                              domain="[('kitchen_screen_user', 'in', ('admin', 'manager', 'cook'))]")

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError(_('Start Date cannot be greater than  End Date'))

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'user_id': self.user_id.id or False,
                'user_name': self.user_id.name or False,
                'offer_type': self.offer_type,
            },
        }

        return self.env.ref('pos_reconciliation_report.invoice_recap_report').report_action(self, data=data)


class ReportAttendanceRecap(models.AbstractModel):
    _name = 'report.pos_reconciliation_report.monthly_recap_report_view'

    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        user_id = data['form']['user_id']
        user_name = data['form']['user_name']
        offer_type = data['form']['offer_type']
        docs = []
        summary = []
        if user_id:
            summary = self.env['pos.session.summary'].search(
                [('session_user', '=', int(user_id)), ('closing_date', '>=', start_date),
                 ('closing_date', '<=', end_date)])
        else:
            summary = self.env['pos.session.summary'].search(
                [('closing_date', '>=', start_date), ('closing_date', '<=', end_date)])
        total_cash = 0
        total_eftpos = 0
        total_expected = 0
        #
        counted_cash = 0
        counted_eftpos = 0
        counted_total = 0

        cash_variance = 0
        eftpos_variance = 0
        total_variance = 0

        total_voucher = 0
        total_discount = 0
        total_loyalty = 0
        total_tips = 0

        sub_total = 0
        total = 0
        for datas in summary:
            total_cash += datas.total_cash
            total_eftpos += datas.total_eftpos
            total_expected += datas.total_expected

            counted_cash += datas.counted_cash
            counted_eftpos += datas.counted_eftpos
            counted_total += datas.counted_total

            cash_variance += datas.cash_variance
            eftpos_variance += datas.eftpos_variance
            total_variance += datas.total_variance

            total_voucher += datas.redeem_card_amount
            total_discount += datas.discount_amount
            total_loyalty += datas.loyalty_points_used
            total_tips += datas.total_tips
        offers = []
        if offer_type:
            for i in summary:
                if i.session.order_ids:
                    if offer_type == 'all':
                        print("all")
                        for lines in i.session.order_ids.lines:
                            if lines.full_product_name == 'Loyalty Benefit':
                                total_loyalty = round(lines.price_subtotal_incl, 2)
                                offers.append({"name": "Loyalty Benefit", "order": lines.order_id.pos_reference,
                                               "session": lines.order_id.session_id.name,
                                               "user": lines.order_id.session_id.user_id.name,
                                               "pos": lines.order_id.session_id.config_id.name,
                                               "price": total_loyalty})
                            if lines.discount > 0:
                                discount_amount = round(lines.price_subtotal_incl * (lines.discount / 100), 2)
                                offers.append({"name": "Product Discount", "order": lines.order_id.pos_reference,
                                               "session": lines.order_id.session_id.name,
                                               "user": lines.order_id.session_id.user_id.name,
                                               "pos": lines.order_id.session_id.config_id.name,
                                               "price": discount_amount})
                            if lines.price_unit < 0:
                                discount_amount = round(lines.price_subtotal_incl, 2)
                                offers.append({"name": "Global Discount", "order": lines.order_id.pos_reference,
                                               "session": lines.order_id.session_id.name,
                                               "user": lines.order_id.session_id.user_id.name,
                                               "pos": lines.order_id.session_id.config_id.name,
                                               "price": np.abs(discount_amount)})
                        for order in i.session.order_ids:
                            if order.redeem_card_amount:
                                redeem = round(order.redeem_card_amount, 2)
                                offers.append({"name": "Coupons", "order": order.pos_reference,
                                               "session": order.session_id.name,
                                               "user": order.session_id.user_id.name,
                                               "pos": order.session_id.config_id.name,
                                               "price": redeem})
                    elif offer_type == 'coupon_promotion':
                        print("coupon")
                        for order in i.session.order_ids:
                            if order.redeem_card_amount:
                                redeem = round(order.redeem_card_amount, 2)
                                offers.append({"name": "Coupons", "order": order.pos_reference,
                                               "session": order.session_id.name,
                                               "user": order.session_id.user_id.name,
                                               "pos": order.session_id.config_id.name,
                                               "price": redeem})
                    elif offer_type == 'loyalty':
                        print("Loyalty")
                        for lines in i.session.order_ids.lines:
                            if lines.full_product_name == 'Loyalty Benefit':
                                total_loyalty = round(lines.price_subtotal_incl, 2)
                                offers.append({"name": "Loyalty Benefit", "order": lines.order_id.pos_reference,
                                               "session": lines.order_id.session_id.name,
                                               "user": lines.order_id.session_id.user_id.name,
                                               "pos": lines.order_id.session_id.config_id.name,
                                               "price": total_loyalty})
                    elif offer_type == 'discount':
                        print("discount")
                        for lines in i.session.order_ids.lines:
                            if lines.discount > 0:
                                discount_amount = round(lines.price_subtotal_incl * (lines.discount / 100), 2)
                                offers.append({"name": "Product Discount", "order": lines.order_id.pos_reference,
                                               "session": lines.order_id.session_id.name,
                                               "user": lines.order_id.session_id.user_id.name,
                                               "pos": lines.order_id.session_id.config_id.name,
                                               "price": discount_amount})

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': start_date,
            'date_end': end_date,
            'user_name': user_name,
            'summary': summary,
            'total_cash': round(total_cash, 2),
            'total_eftpos': round(total_eftpos, 2),
            'total_expected': round(total_expected, 2),
            'counted_cash': round(counted_cash, 2),
            'counted_eftpos': round(counted_eftpos, 2),
            'counted_total': round(counted_total, 2),
            'cash_variance': round(cash_variance, 2),
            'eftpos_variance': round(eftpos_variance, 2),
            'total_voucher': round(total_voucher, 2),
            'total_discount': round(total_discount, 2),
            'total_loyalty': round(total_loyalty, 2),
            'total_tips': round(total_tips, 2),
            'total_variance': round(total_variance, 2),
            'sub_total': round(sub_total, 2),
            'total': round(total, 2),
            'offers': offers,
            'offers_length': len(offers),
            'docs': docs,
        }
