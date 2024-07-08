import datetime
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from odoo.exceptions import AccessError
import numpy as np


class SessionSummaryPOS(models.Model):
    _name = 'pos.session.summary'
    _order = 'session desc'
    _rec_name = 'session'

    session = fields.Many2one('pos.session', string="Session")
    session_user = fields.Many2one('res.users', string="User")
    starting_balance = fields.Float(string="Opening Balance")
    opening_date = fields.Datetime(string="Opening Date")
    orders_count = fields.Float(string="Orders Count")
    total_payments_amount = fields.Float(string="Payment Amount")
    total_cash = fields.Float(string="Cash Payment")
    total_eftpos = fields.Float(string="EftPOS Payment")
    total_expected = fields.Float(string="Total Expected Payment")
    total_tips = fields.Float(string="Total Tips")

    counted_cash = fields.Float(string="Counted Cash Payment")
    counted_eftpos = fields.Float(string="Counted EftPOS Payment")
    counted_total = fields.Float(string="Total Counted Payment")

    cash_variance = fields.Float(string="Cash Variance")
    eftpos_variance = fields.Float(string="EftPOS Variance")
    total_variance = fields.Float(string="Total Variance")

    payments_and_opening_balance = fields.Float(string="Opening Balance + Payments")
    closing_date = fields.Datetime('Closing Date')

    pos_config = fields.Many2one('pos.config')
    journal_entries = fields.Many2one('account.move')

    redeem_card_amount = fields.Float(string="Gift Card Redeem")
    discount_amount = fields.Float(string="Discount Amount")
    loyalty_points_used = fields.Float(string="Loyalty Points Used")


class POSSession(models.Model):
    _inherit = 'pos.order'

    @api.model
    def CheckUnpaidOpenOrders(self, current_session):
        session = self.env['pos.session'].sudo().search([('id', '=', int(current_session))])
        open_order = False
        if session:
            if session.order_ids:
                for i in session.order_ids:
                    if i.state == 'draft' and i.delivery_type == 'phone':
                        open_order = True
                        break
                    else:
                        pass
        print("OPEN ORDER", open_order)
        return open_order

    @api.model
    def load_session_details(self, current_session):
        lines = []
        data = {}
        session = self.env['pos.session'].sudo().search([('id', '=', int(current_session))])
        if session.user_id.kitchen_screen_user != 'admin':
            session.action_pos_session_closing_control()
            return False
        if session:
            orders = session.order_ids
            pos_orders = []
            total_cash = 0.0
            total_efpos = 0.0
            total_discount = 0.0
            total_redeem = 0.0
            total_loyalty = 0.0
            total_tips = 0.0
            data['id'] = session.id
            data['user_id'] = session.user_id.id
            data['user_name'] = session.user_id.name
            data['pos_id'] = session.config_id.id
            data['pos_name'] = session.config_id.name
            data['starting_balance'] = round(session.cash_register_balance_start, 2)
            data['opening_date'] = session.start_at
            data['total_payments_amount'] = session.total_payments_amount
            data['orders_count'] = session.order_count
            if orders:
                payments = self.env['pos.payment'].sudo().search([('session_id', '=', int(session.id))])
                for amount in payments:
                    if amount.payment_method_id.name == 'Cash':
                        total_cash = total_cash + amount.amount
                    else:
                        total_efpos = total_efpos + amount.amount
                for order in orders:
                    if order.redeem_card_amount:
                        total_redeem = total_redeem + order.redeem_card_amount
                    if order.lines:
                        for line in order.lines:
                            if line.full_product_name == 'Loyalty Benefit':
                                total_loyalty = total_loyalty + line.price_subtotal_incl
                            if line.discount > 0:
                                discount_amount = line.price_subtotal_incl * (line.discount / 100)
                                total_discount = total_discount + discount_amount
                            if line.full_product_name == 'Tips':
                                total_tips = total_tips + line.price_subtotal_incl
                            if line.price_unit < 0:
                                global_discount_amount = np.abs(line.price_subtotal_incl)
                                total_discount = total_discount + global_discount_amount
            data['total_cash'] = round(total_cash, 2)
            data['total_efpos'] = round(total_efpos, 2)
            data['total_redeem'] = round(total_redeem, 2)
            data['total_discount'] = round(total_discount, 2)
            data['total_loyalty'] = round(total_loyalty, 2)
            data['total_tips'] = round(total_tips, 2)

            data['variance_cash'] = 0 - round(total_cash, 2)
            data['variance_eftpos'] = 0 - round(total_efpos, 2)
            data['total_variance'] = 0 - round(total_efpos, 2) + 0 - round(total_cash, 2)
            data['total_variance'] = round(0 - round(total_efpos, 2) + 0 - round(total_cash, 2), 2)

            data['total_discount'] = round(total_discount, 2)
            data['total_expected'] = round(round(total_cash, 2) + round(total_efpos, 2), 2)
            total = round(total_cash, 2) + round(total_efpos, 2)
        return data

    @api.model
    def printAndClose(self, current_session, counted_cash, counted_eftpos, counted_total, cash_variance,
                      eftpos_variance, total_variance, opening_balance_value, total_voucher, total_discount,
                      total_loyalty_amount, total_tips_amount):
        # try:
        lines = []
        data = {}
        vals = {}

        session = self.env['pos.session'].sudo().search([('id', '=', int(current_session))])
        if session:
            orders = session.order_ids
            pos_orders = []
            total_cash = 0.0
            total_efpos = 0.0
            total_discount = 0.0
            total_tips = 0.0
            total_loyalty = 0.0
            voucher_redeem_amount = 0.0
            data['id'] = session.id
            data['user_id'] = session.user_id.id
            data['user_name'] = session.user_id.name
            data['pos_id'] = session.config_id.id
            data['pos_name'] = session.config_id.name
            data['starting_balance'] = round(session.cash_register_balance_start, 2)

            data['opening_date'] = session.start_at
            data['total_payments_amount'] = session.total_payments_amount
            data['orders_count'] = session.order_count
            if orders:
                payments = self.env['pos.payment'].sudo().search([('session_id', '=', int(session.id))])
                for amount in payments:
                    if amount.payment_method_id.name == 'Cash':
                        total_cash = total_cash + amount.amount
                    else:
                        total_efpos = total_efpos + amount.amount
                for order in orders:
                    if order.lines:
                        # for line in order.lines:
                        voucher_redeem_amount = round(order.redeem_card_amount, 2)
                        for line in order.lines:
                            if line.full_product_name == 'Loyalty Benefit':
                                total_loyalty = total_loyalty + line.price_subtotal_incl
                            if line.discount > 0:
                                discount_amount = line.price_subtotal_incl * (line.discount / 100)
                                total_discount = total_discount + discount_amount
                            if line.full_product_name == 'Tips':
                                total_tips = total_tips + line.price_subtotal_incl
                            if line.price_unit < 0:
                                global_discount_amount = np.abs(line.price_subtotal_incl)
                                total_discount = total_discount + global_discount_amount
            data['total_cash'] = round(total_cash, 2)
            data['total_efpos'] = round(total_efpos, 2)

            data['variance_cash'] = 0 - round(total_cash, 2)
            data['variance_eftpos'] = 0 - round(total_efpos, 2)
            data['total_variance'] = 0 - round(total_efpos, 2) + 0 - round(total_cash, 2)

            data['total_discount'] = round(total_discount, 2)
            data['total_expected'] = round(total_cash, 2) + round(total_efpos, 2)
            total = round(total_cash, 2) + round(total_efpos, 2)

            data['float_total'] = round(session.cash_register_balance_start, 2) + round(total, 2)

            data['counted_cash'] = counted_cash
            data['counted_eftpos'] = counted_eftpos
            data['counted_total'] = counted_total
            data['cash_variance'] = cash_variance
            data['eftpos_variance'] = eftpos_variance
            data['total_variance'] = total_variance

            vals['counted_cash'] = counted_cash
            vals['counted_eftpos'] = counted_eftpos
            vals['counted_total'] = counted_total
            vals['cash_variance'] = cash_variance
            vals['eftpos_variance'] = eftpos_variance
            vals['total_variance'] = total_variance
            vals['redeem_card_amount'] = voucher_redeem_amount
            vals['discount_amount'] = total_discount
            vals['loyalty_points_used'] = total_loyalty_amount
            vals['total_tips'] = total_tips_amount

            vals['session'] = current_session
            vals['session_user'] = session.user_id.id
            vals['starting_balance'] = opening_balance_value
            vals['opening_date'] = session.start_at

            vals['orders_count'] = session.order_count
            vals['total_payments_amount'] = session.total_payments_amount
            vals['total_cash'] = round(total_cash, 2)
            vals['total_eftpos'] = round(total_efpos, 2)
            vals['total_expected'] = round(total_cash, 2) + round(total_efpos, 2)

            vals['payments_and_opening_balance'] = round(float(opening_balance_value), 2) + round(total, 2)
            vals['pos_config'] = session.config_id.id

        if session.order_ids:
            order_obj = self.env['pos.order']
            order_ids = [order.id for order in session.order_ids if order.state == 'draft']

            if order_ids:
                self.env.cr.execute(''' select id from account_bank_statement_line
                                WHERE pos_statement_id in %s''' % (
                        " (%s) " % ','.join(map(str, order_ids))))
                result = self.env.cr.dictfetchall()
                if len(order_ids) == 1:
                    order_ids.append(0)
                self.env.cr.execute("delete from pos_payment where pos_order_id in %s", (tuple(order_ids),))
                self.env.cr.commit()
                for statement_line in result:
                    statement_line = self.env['account.bank.statement.line'].browse([statement_line.get('id')])
                    if statement_line.journal_entry_ids:
                        move_lines = []
                        move_ids = []
                        for move_line in statement_line.journal_entry_ids:
                            move_lines.append(move_line.id)
                            move_ids.append(move_line.move_id.id)
                        if move_lines:
                            del_rec_line = ''' delete from account_partial_reconcile
                                                    WHERE credit_move_id in %s or debit_move_id in %s''' % (
                                " (%s) " % ','.join(map(str, move_lines)),
                                " (%s) " % ','.join(map(str, move_lines)))
                            self.env.cr.execute(del_rec_line)
                        if move_ids:
                            del_move = ''' delete from account_move
                                                    WHERE id in %s''' % (
                                    " (%s) " % ','.join(map(str, move_ids)))
                            self.env.cr.execute(del_move)
                            self.env.cr.commit()
                once = False
                total_amount = sum(
                    order_obj.browse(order_ids).filtered(lambda x: x.state == 'done').mapped(
                        'amount_total'))
                orders = order_obj.browse(order_ids)
                session_ids = list(set([order.session_id for order in orders]))
                picking_ids = []
                for order in orders:
                    for p in order.picking_ids:
                        picking_ids.append(p.id)
                statements = list(
                    set([statement_id for session_id in session_ids for statement_id in session_id.statement_ids]))
                del_rec_line = ''' delete from pos_order
                                            WHERE id in %s''' % (" (%s) " % ','.join(map(str, order_ids)))
                self.env.cr.execute(del_rec_line)
                if picking_ids:
                    del_pack_line = ''' delete from stock_move_line
                                                WHERE picking_id in %s''' % (" (%s) " % ','.join(map(str, picking_ids)))
                    self.env.cr.execute(del_pack_line)
                    del_move_line = ''' delete from stock_move
                                                WHERE picking_id in %s''' % (" (%s) " % ','.join(map(str, picking_ids)))
                    self.env.cr.execute(del_move_line)
                    del_picking_line = ''' delete from stock_picking
                                                WHERE id in %s''' % (" (%s) " % ','.join(map(str, picking_ids)))
                    self.env.cr.execute(del_picking_line)
                for each_stat in statements:
                    each_stat._end_balance()
                    if each_stat.state == 'confirm':
                        each_stat.write({'balance_end_real': each_stat.balance_end_real - total_amount})
        close_session = session.action_pos_session_closing_control()
        summary = self.env['pos.session.summary']
        vals['closing_date'] = session.stop_at
        vals['journal_entries'] = session.move_id.id
        closed_session = summary.sudo().create(vals)
        session.sudo().write({'cash_register_balance_start': opening_balance_value})
        return True
    # except:
    #     return False

