import logging
import pytz

from odoo.exceptions import AccessDenied
from odoo.http import request
from odoo import api, fields, models, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class ApprovalException(Exception):
    def __init__(self, message="User account is not approved"):
        self.message = message
        super().__init__(self.message)


class User(models.Model):
    _inherit = 'res.users'

    approval = fields.Selection([
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked')],
        default='waiting',
        string='Approval Status')

    def action_approve_user(self):
        self.approval = self.env.context.get('approval')

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        """Function replaced to check approval status and raise exception if necessary"""
        res = super(User, cls)._login(db, login, password, user_agent_env)
        self = api.Environment(request.env.cr, SUPERUSER_ID, {})[cls._name]
        user = self.sudo().browse(res)
        if user.groups_id.filtered(lambda x: x.category_id.name == 'User types' and x.name == 'Portal'):
            if user.approval == 'blocked':
                raise ApprovalException(message='This user account is blocked.')
            elif user.approval == 'rejected':
                raise ApprovalException(message='This user account application is rejected.')
            elif user.approval == 'waiting':
                raise ApprovalException(message='This user account application is waiting for approval.')
        return user.id
