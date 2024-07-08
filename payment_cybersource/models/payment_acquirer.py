from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('cyber', 'Cyber')], ondelete={'cyber': 'set default'})
    cybersource_merchant_id = fields.Char(required_if_provider='cybersource', string="Cybersource Merchant id")
    cybersource_key = fields.Char(required_if_provider='cybersource', string="cybersource Key")

    @api.depends('provider')
    def _compute_view_configuration_fields(self):
        super()._compute_view_configuration_fields()
        self.filtered(lambda acq: acq.provider == 'cyber').show_credentials_page = False

    # @api.constrains('state', 'provider')
    # def _check_acquirer_state(self):
    #     print('_check_acquirer_state')
    #     if self.filtered(lambda a: a.provider == 'cyber' and a.state not in ('test', 'disabled')):
    #         raise UserError(_("Test acquirers should never be enabled."))

    def _get_default_payment_method_id(self):
        print('_get_default_payment_method_id')
        self.ensure_one()
        if self.provider != 'cyber':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_cybersource.payment_method_cyber').id


class ResCompany(models.Model):
    _inherit = 'res.company'

    cybersource_merchant_id = fields.Char('Merchant id Cybersource', default="dummy")
    cybersource_org_id = fields.Selection([
                                            ('1snn5n9w', 'Test Enviroment'),
                                            ('k8vif92e', 'Prod Enviroment'),
                                        ], string="Org ID")
