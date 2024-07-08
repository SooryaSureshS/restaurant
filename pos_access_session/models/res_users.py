# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    pos_access_session = fields.Boolean(
        'POS Access all Sessions',
        default=0)


class POSSessions(models.Model):
    _inherit = "pos.session"

    def open_frontend_cb(self):
        uid = self._uid

        user_id = self.env['res.users'].sudo().search([('id', '=', uid)])

        if user_id and user_id.id == self.user_id.id:
            return super(POSSessions, self).open_frontend_cb()
        elif user_id.pos_access_session:
            return super(POSSessions, self).open_frontend_cb()
        else:
            raise UserError(
                _(
                    "You are not authorized to continue this session. Please contact your administrator. "
                )
            )

    def action_pos_session_closing_control(self):
        uid = self.user_id
        user_id = self.env['res.users'].sudo().search([('id', '=', uid.id)])

        if user_id.id == self.user_id.id or user_id.pos_access_session:

            self._check_pos_session_balance()
            for session in self:
                if any(order.state == 'draft' for order in session.order_ids):
                    raise UserError(_("You cannot close the POS when orders are still in draft"))
                if session.state == 'closed':
                    raise UserError(_('This session is already closed.'))
                session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
                if not session.config_id.cash_control:
                    data = self.load_session_details(self.id)
                    session_data = self.env['pos.session.wizard']
                    closed_session = session_data.sudo().create(data)
                    view_item = [(self.env.ref('pos_access_session.wizard_session_summary_wizard').id, 'form')]
                    view = self.env.ref('pos_access_session.wizard_session_summary_wizard')
                    return {
                        'name': _('Session Summary'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'pos.session.wizard',
                        'views': view_item,
                        'view_id': view.id,
                        'res_id': closed_session.id,
                        'target': 'new',
                        'context': {
                            'default_session': self.id,
                        }
                    }
        else:
            raise UserError(
                _(
                    "You are not authorized to close this session. Please contact your administrator. "
                )
            )

    def action_pos_session_validate(self):

        uid = self.user_id
        user_id = self.env['res.users'].sudo().search([('id', '=', uid.id)])

        if user_id and user_id.id == self.user_id.id:
            s = self.show_wizard()
            return super(POSSessions, self).action_pos_session_validate()
        elif user_id.pos_access_session:
            s = self.show_wizard()
            return super(POSSessions, self).action_pos_session_validate()
        else:
            raise UserError(
                _(
                    "You are not authorized to close this session. Please contact your administrator. "
                )
            )

    def load_session_details(self, current_session):
        lines = []
        data = {}
        session = self.env['pos.session'].sudo().search([('id', '=', int(current_session))])
        if session:
            orders = session.order_ids
            pos_orders = []
            total_cash = 0.0
            total_eftpos = 0.0
            total_discount = 0.0
            total_redeem = 0.0
            total_loyalty = 0.0
            total_tips = 0.0
            data['session'] = session.id
            data['session_user'] = session.user_id.id
            data['pos_config'] = session.config_id.id
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
                        total_eftpos = total_eftpos + amount.amount
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

            data['total_cash'] = round(total_cash, 2)
            data['total_eftpos'] = round(total_eftpos, 2)
            data['redeem_card_amount'] = round(total_redeem, 2)
            data['discount_amount'] = round(total_discount, 2)
            data['loyalty_points_used'] = round(total_loyalty, 2)
            data['total_tips'] = round(total_tips, 2)

            data['cash_variance'] = 0 - round(total_cash, 2)
            data['eftpos_variance'] = 0 - round(total_eftpos, 2)
            data['total_variance'] = round(0 - round(total_eftpos, 2) + 0 - round(total_cash, 2), 2)

            data['total_expected'] = round(round(total_cash, 2) + round(total_eftpos, 2), 2)
            total = round(total_cash, 2) + round(total_eftpos, 2)
            # data['closing_date'] = session.stop_at
            data['journal_entries'] = session.move_id.id

        return data

    def show_wizard(self):
        data = self.load_session_details(self.id)
        # self.session_data_wizard(data)
        session_data = self.env['pos.session.wizard']
        closed_session = session_data.sudo().create(data)
        view_item = [(self.env.ref('pos_access_session.wizard_session_summary_wizard').id, 'form')]
        view = self.env.ref('pos_access_session.wizard_session_summary_wizard')
        return {
            'name': _('Session Summary'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'pos.session.wizard',
            'views': view_item,
            'view_id': view.id,
            'target': 'new',
            'context': {
                'default_session': self.id,
            }
        }


class POSSessionWizard(models.TransientModel):
    _name = "pos.session.wizard"
    _description = "POS Summary"

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


    @api.onchange('counted_cash')
    def onchange_counted_cash(self):
        counted_cash = self.counted_cash
        total_cash = self.total_cash
        cash_variance = counted_cash - total_cash
        self.cash_variance = round(cash_variance, 2)
        self.counted_total = round(self.counted_eftpos + counted_cash, 2)
        self.total_variance = round(cash_variance + self.eftpos_variance, 2)

    @api.onchange('counted_eftpos')
    def onchange_counted_eftpos(self):
        counted_eftpos = self.counted_eftpos
        total_eftpos = self.total_eftpos
        eftpos_variance = counted_eftpos - total_eftpos
        self.eftpos_variance = round(eftpos_variance, 2)
        self.counted_total = round(counted_eftpos + self.counted_cash, 2)
        self.total_variance = round(self.cash_variance + eftpos_variance, 2)


    def create_session_data(self):
        # try:
            vals = {}
            vals['counted_cash'] = self.counted_cash
            vals['counted_eftpos'] = self.counted_eftpos
            vals['counted_total'] = self.counted_total
            vals['cash_variance'] = self.cash_variance
            vals['eftpos_variance'] = self.eftpos_variance
            vals['total_variance'] = self.total_variance
            vals['redeem_card_amount'] = self.redeem_card_amount
            vals['discount_amount'] = self.discount_amount
            vals['loyalty_points_used'] = self.loyalty_points_used
            vals['total_tips'] = self.total_tips

            vals['session'] = self.session.id
            vals['session_user'] = self.session.user_id.id
            vals['starting_balance'] = self.starting_balance
            vals['opening_date'] = self.session.start_at

            vals['orders_count'] = self.orders_count
            vals['total_payments_amount'] = self.total_payments_amount
            vals['total_cash'] = round(self.total_cash, 2)
            vals['total_eftpos'] = round(self.total_eftpos, 2)
            vals['total_expected'] = round(self.total_cash, 2) + round(self.total_eftpos, 2)
            total = round(self.total_cash, 2) + round(self.total_eftpos, 2)

            vals['payments_and_opening_balance'] = round(float(self.starting_balance), 2) + round(total, 2)
            vals['pos_config'] = self.session.config_id.id
            session_data = self.env['pos.session.summary'].sudo().search([('session.id', '=', self.session.id)])

            if session_data:
                self.session.action_pos_session_close()
                pass
            else:
                self.session.action_pos_session_close()
                vals['closing_date'] = self.session.stop_at
                vals['journal_entries'] = self.session.move_id.id
                summary = self.env['pos.session.summary']
                closed_session = summary.sudo().create(vals)
                self.session.sudo().write({'cash_register_balance_start': round(self.starting_balance, 2)})

        # except:
        #     pass