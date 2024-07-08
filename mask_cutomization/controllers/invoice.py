from odoo import http
from odoo.http import request


class WebsitePreviewDesign(http.Controller):

    @http.route('/my/invoice/<int:oid>', type="http", website=True, auth='public')
    def submit_packaging_carton(self,  oid):
        order = request.env['sale.order'].sudo().browse(int(oid))
        return request.render("mask_cutomization.account_invoice", {'order': order})
