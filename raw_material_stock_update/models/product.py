# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_inventory_adjust_date(self):
        return fields.Date.context_today

    is_raw_material = fields.Boolean('Recipe')
    stock_update_type = fields.Selection(string='Stock Update Type',
                                         selection=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])

    stock_update_type_daily = fields.Boolean('Stock Update Daily')
    stock_update_type_week = fields.Boolean('Stock Update Weekly')
    stock_update_type_monthly = fields.Boolean('Stock Update Monthly')
    carton = fields.Float(string='Carton')
    sleeve = fields.Float(string='Sleeve')
    raw_material_ids = fields.One2many('raw.material', 'recipe_id', string="Raw Material")
    inventory_location_id = fields.Many2one('stock.location', string="Recipe Location")
    theoretical_carton = fields.Float(string='Theoretical Carton')
    theoretical_sleeve = fields.Float(string='Theoretical Sleeve')
    carton_variance = fields.Float(string='Carton Variance (%)')
    sleeve_variance = fields.Float(string='Sleeve Variance (%)')
    new_quantity = fields.Float(string='Quantity')
    inventory_adjust_date = fields.Date('Inventory Adjust date', default=fields.Date.today)
    rel_inventory_adjust_date = fields.Date('Inventory Adjust Date', related='inventory_adjust_date')

    @api.constrains('new_quantity')
    def check_new_quantity(self):
        if any(record.new_quantity < 0 for record in self):
            raise UserError(_('Quantity cannot be negative.'))

    @api.onchange('sleeve', 'carton')
    def onchange_sleeve_carton(self):
        for product in self:
            if product.carton < product.theoretical_carton:
                carton_variance = (product.carton / product.theoretical_carton) * 100
                product.write({'carton_variance': carton_variance})
            else:
                product.write({'carton_variance': 0.0})

            if product.sleeve < product.theoretical_sleeve:
                sleeve_variance = (product.sleeve / product.theoretical_sleeve) * 100
                product.write({'sleeve_variance': sleeve_variance})
            else:
                product.write({'sleeve_variance': 0.0})

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        total = 0
        if self.raw_material_ids:
            raw_ids = self.env['raw.material'].search([('id', 'in', self.raw_material_ids.ids)])
            for rec in raw_ids:
                total += rec.recipe_cost
            self.product_variant_id.standard_price = total
        return res

    @api.onchange('standard_price')
    def cost_validation(self):
        if self.raw_material_ids:
            raise ValidationError(_("Cost price cannot be changed"))

    # @api.onchange('stock_update_type')
    # def onchange_stock_update_type(self):
    #    for product in self:
    #        if product.stock_update_type == 'daily':
    #            product.write({'inventory_adjust_date': datetime.today() + timedelta(days=1)})
    #            # product.inventory_adjust_date = datetime.today() + timedelta(days=1)
    #        if product.stock_update_type == 'weekly':
    #            product.write({'inventory_adjust_date': datetime.today() + timedelta(weeks=1)})
    #        if product.stock_update_type == 'monthly':
    #            product.write({'inventory_adjust_date': datetime.today() + timedelta(days=30)})

    # def write(self, vals):
    #    res = super(ProductTemplate, self).write(vals)
    #    for template_obj in self:
    #        if 'new_quantity' in vals:
    #            if template_obj.type == 'product':
    #                quant_line = {
    #                    "product_id": template_obj.product_variant_id.id,
    #                    "quantity": template_obj.new_quantity,
    #                    "location_id": template_obj.inventory_location_id.id,
    #                }
    #                self.env["stock.quant"].sudo().create(quant_line)
    #    return res


# class ProductpProduct(models.Model):
#    _inherit = 'product.product'

# @api.onchange('stock_update_type')
# def onchange_stock_update_type(self):
#    for product in self:
#        if product.stock_update_type == 'daily':
#            product.write({'inventory_adjust_date': datetime.today() + timedelta(days=1)})
#            # product.inventory_adjust_date = datetime.today() + timedelta(days=1)
#        if product.stock_update_type == 'weekly':
#            product.write({'inventory_adjust_date': datetime.today() + timedelta(weeks=1)})
#        if product.stock_update_type == 'monthly':
#            product.write({'inventory_adjust_date': datetime.today() + timedelta(days=30)})


class RawMaterial(models.Model):
    _name = 'raw.material'
    _description = "Raw Material"

    recipe_id = fields.Many2one("product.template", ondelete='cascade', string="Raw materials")
    product_id = fields.Many2one("product.template", string="Ingredient name")
    default_code = fields.Char(related='product_id.default_code', string="Number")
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string="Unit")
    product_qty = fields.Float(string="Quantity")
    unit_price = fields.Float(related='product_id.standard_price', string="Unit Cost")
    recipe_cost = fields.Float(string="Recipe Cost", compute="_compute_recipe_cost")

    @api.depends('product_qty', 'unit_price')
    def _compute_recipe_cost(self):
        for i in self:
            i.recipe_cost = i.unit_price * i.product_qty


