from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class POSSessionWizardEmpyeePin(models.TransientModel):
    _name = "pos.employee.wizard"
    _description = "POS Employee"

    pin = fields.Char(string='Employee Pin')

    def check_pin(self):
        if self.pin:
            uid = request.session.uid
            user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
            employoee = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
            if not employoee:
                raise ValidationError(_("No employee found for this user."))
            else:
                if int(employoee.pin) == int(self.pin):
                    # data = self.load_session_details(self._context.get('default_session', False))
                    data = self.env['pos.session'].sudo().load_session_details(
                        self._context.get('default_session', False))
                    session_data = self.env['pos.session.wizard']
                    closed_session = session_data.sudo().create(data)
                    view_item = [(self.env.ref('pos_summary_backend.wizard_session_summary_wizard_backend').id, 'form')]
                    view = self.env.ref('pos_summary_backend.wizard_session_summary_wizard_backend')
                    return {
                        'name': _('Session Summary'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'pos.session.wizard',
                        'views': view_item,
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': closed_session.id,

                        'context': {
                            # 'default_id': closed_session.id,
                            # 'default_starting_balance': 100,
                            'default_active_ids': [closed_session.id],
                        }
                    }
                    # self.open_ui(id)
                else:
                    raise ValidationError(_("Wrong Employee Pin."))
        else:
            raise ValidationError(_("Please Enter Pin."))


class POSSessionWizardWizards(models.TransientModel):
    _name = "pos.session.wizard"
    _description = "POS Summary"

    @api.depends('counted_cash', 'starting_balance')
    def compute_amount(self):
        self.bank_deposit_variance = self.counted_cash - self.petty_cash_pull_out
        self.starting_balance = self.starting_balance

    @api.depends('counted_cash', 'starting_balance')
    def compute_expected(self):
        self.total_expected_cash = self.total_cash + self.starting_balance
        self.cash_variance = self.counted_cash - self.total_expected_cash

    @api.depends('counted_eftpos', 'starting_balance')
    def compute_expected_eftpos(self):
        self.total_expected_eftpos = self.total_eftpos
        self.eftpos_variance = self.counted_eftpos - self.total_expected_eftpos
        self.total_eftpos = self.counted_eftpos

    name = fields.Char(string='name', default='ddddd')
    hide = fields.Boolean(string='Hide')
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

    float_amount = fields.Float(string="Float Amount")
    # subtotal = fields.Float(string="Subtotal")
    # cash_back = fields.Float(string="Cash Back")

    cash_2000_count = fields.Integer(string="$2000")
    cash_500_count = fields.Integer(string="$500")
    cash_100_count = fields.Integer(string="$100")
    cash_50_count = fields.Integer(string="$50")
    cash_20_count = fields.Integer(string="$20")
    cash_10_count = fields.Integer(string="$10")
    cash_5_count = fields.Integer(string="$5")
    cash_2_count = fields.Integer(string="$2")
    cash_1_count = fields.Integer(string="$1")
    cash_50c_count = fields.Integer(string="50c")
    cash_20c_count = fields.Integer(string="50c")
    cash_10c_count = fields.Integer(string="10c")
    cash_5c_count = fields.Integer(string="5c")

    cash_2000 = fields.Float()
    cash_500 = fields.Float()
    cash_100 = fields.Float()
    cash_50 = fields.Float()
    cash_20 = fields.Float()
    cash_10 = fields.Float()
    cash_5 = fields.Float()
    cash_2 = fields.Float()
    cash_1 = fields.Float()
    cash_50c = fields.Float()
    cash_20c = fields.Float()
    cash_10c = fields.Float()
    cash_5c = fields.Float()
    cash_unit = fields.Char('Cash unit')
    cash_subunit = fields.Char('Cash unit')
    petty_cash_pull_out = fields.Float('Petty cash pull out')
    bank_deposit = fields.Float('Bank deposit')
    bank_deposit_variance = fields.Float(compute=compute_amount, string='Bank deposit varience')
    insert_bag_number = fields.Char('Insert Bag Number')
    total_expected_cash = fields.Float(compute=compute_expected, string='Expected Cash')
    total_expected_eftpos = fields.Float(compute=compute_expected_eftpos, string='Expected EFT')

    @api.onchange('starting_balance')
    def action_starting_balance(self):
        print("seeeee", self.starting_balance)
        self.write({
            'float_amount': self.starting_balance
        })

    @api.onchange(
        'cash_2000_count', 'cash_500_count', 'cash_100_count', 'cash_50_count',
        'cash_20_count', 'cash_10_count', 'cash_5_count', 'cash_2_count', 'cash_1_count',
        'cash_50c_count', 'cash_20c_count', 'cash_10c_count', 'cash_5c_count')
    def action_cash_count(self):
        self.cash_2000 = self.cash_2000_count * 2000
        self.cash_500 = self.cash_500_count * 500
        self.cash_100 = self.cash_100_count * 100
        self.cash_50 = self.cash_50_count * 50
        self.cash_20 = self.cash_20_count * 20
        self.cash_10 = self.cash_10_count * 10
        self.cash_5 = self.cash_5_count * 5
        self.cash_2 = self.cash_2_count * 2
        self.cash_1 = self.cash_1_count * 1

        self.cash_50c = self.cash_50c_count * .50
        self.cash_20c = self.cash_20c_count * .20
        self.cash_10c = self.cash_10c_count * .10
        self.cash_5c = self.cash_5c_count * .05
        self.counted_cash = self.cash_2000 + self.cash_500 + self.cash_100 + self.cash_50 + self.cash_20 + self.cash_10 + self.cash_5 + self.cash_2 + self.cash_1 + self.cash_50c + self.cash_20c + self.cash_10c + self.cash_5c

    # @api.onchange('counted_cash')
    def action_count_cash(self):
        print("counted", self.hide)
        self.write({
            'hide': True
        })
        view_item = [(self.env.ref('pos_summary_backend.wizard_session_summary_wizard_backend').id, 'form')]
        view = self.env.ref('pos_summary_backend.wizard_session_summary_wizard_backend')

        return {
            'name': _('Session Summary'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'pos.session.wizard',
            'views': view_item,
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,

            'context': {
                # 'default_id': closed_session.id,
                # 'default_starting_balance': 100,
                'default_active_ids': [self.id],
            }
        }

    # @api.onchange('counted_cash')
    # def onchange_counted_cash(self):
    #     counted_cash = self.counted_cash
    #     total_cash = self.total_cash
    #     cash_variance = counted_cash - total_cash
    #     self.cash_variance = round(cash_variance, 2)
    #     self.counted_total = round(self.counted_eftpos + counted_cash, 2)
    #     self.total_variance = round(cash_variance + self.eftpos_variance, 2)

    @api.onchange('counted_eftpos')
    def onchange_counted_eftpos(self):
        counted_eftpos = self.counted_eftpos
        total_eftpos = self.total_eftpos
        eftpos_variance = counted_eftpos - total_eftpos
        self.eftpos_variance = round(eftpos_variance, 2)
        self.counted_total = round(counted_eftpos + self.counted_cash, 2)
        self.total_variance = round(self.cash_variance + eftpos_variance, 2)

    # def create_session_data(self):
    #     print("dfdfdfdf")

    def create_session_data(self):
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
        vals['pos_config'] = self.session.config_id.id
        vals['petty_cash_pull_out'] = self.petty_cash_pull_out
        vals['bank_deposit_variance'] = self.counted_cash - self.starting_balance
        vals['insert_bag_number'] = self.insert_bag_number
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
            self.session.sudo().write({
                'cash_register_balance_start': round(self.starting_balance, 2),
                'session_summary': closed_session.id,
                'session_summary_boolean': True,
                'stop_at': fields.Datetime.now(),
            })
