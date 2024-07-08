from odoo import http
from odoo.http import request


class SignupForm(http.Controller):

    @http.route('/country/change', type='json', auth="public", methods=['POST'],
                website=True, csrf=False)
    def country_change(self, **kwargs):
        states = []
        if kwargs.get('country'):
            country = request.env['res.country'].sudo().browse(int(kwargs.get('country')))
            if country and country.state_ids:
                states = [{'id': state.id, 'name': state.name} for state in country.state_ids]
        return states
