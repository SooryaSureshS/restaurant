import logging
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, _
from odoo.http import request
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_cart_recovery_template(self):
        """
        Return the cart recovery template record for a set of orders.
        If they all belong to the same website, we return the website-specific template;
        otherwise we return the default template.
        If the default is not found, the empty ['mail.template'] is returned.
        """
        websites = self.mapped('website_id')
        template = self.env.ref('template_abandoned_cart.mail_template_sale_cart_recovery_onit', raise_if_not_found=False)
        return template or self.env['mail.template']


class Website(models.Model):
    _inherit = 'website'

    def _default_recovery_mail_template(self):
        try:
            return self.env.ref('template_abandoned_cart.mail_template_sale_cart_recovery_onit').id
        except ValueError:
            return False

class Rescompany(models.Model):
    _inherit = 'res.company'

    cart_email=fields.Boolean(string="Personalize Cart Email")