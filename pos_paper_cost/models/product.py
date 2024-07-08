from odoo import fields,models,api,_


class ProductTemplate(models.Model):
    _inherit = "product.template"

    paper_size_id = fields.Many2one('product.product', string="Paper Size")
