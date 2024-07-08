from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class SaleConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    holiday_surcharge = fields.Boolean("Holiday surcharge")
    surcharge_product = fields.Many2one("product.product", string='Surcharge Product')
    start_date = fields.Date(string="Start date", readonly=False)
    end_date = fields.Date(string="End date", readonly=False)
    choose_price = fields.Selection([
        ('percentage', 'Percentage'),
        ('amount', 'Amount')
    ], string="Choose pricing method", readonly=False)
    percentage = fields.Float("Percentage", readonly=False)
    amount = fields.Float("Amount", readonly=False)

    def get_values(self):
        res = super(SaleConfig, self).get_values()
        res.update(
            start_date =self.env['ir.config_parameter'].sudo().get_param(
                'bi_website_add_product.start_date'),
            end_date=self.env['ir.config_parameter'].sudo().get_param(
                'bi_website_add_product.end_date'),
            choose_price=self.env['ir.config_parameter'].sudo().get_param(
                'bi_website_add_product.choose_price'),
            percentage=self.env['ir.config_parameter'].sudo().get_param(
                'bi_website_add_product.percentage'),
            amount=self.env['ir.config_parameter'].sudo().get_param(
                'bi_website_add_product.amount'),
            holiday_surcharge=self.env['ir.config_parameter'].sudo().get_param(
                'bi_website_add_product.holiday_surcharge'),
            surcharge_product=int(self.env['ir.config_parameter'].sudo().get_param(
                'bi_website_add_product.surcharge_product')),
        )
        return res

    def set_values(self):
        super(SaleConfig, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        start_date = self.start_date
        end_date = self.end_date
        choose_price = self.choose_price
        amount = self.amount
        percentage = self.percentage
        holiday_surcharge = self.holiday_surcharge
        surcharge_product = self.surcharge_product.id
        param.set_param('bi_website_add_product.start_date', start_date)
        param.set_param('bi_website_add_product.end_date', end_date)
        param.set_param('bi_website_add_product.percentage', percentage)
        param.set_param('bi_website_add_product.choose_price', choose_price)
        param.set_param('bi_website_add_product.amount', amount)
        param.set_param('bi_website_add_product.holiday_surcharge', holiday_surcharge)
        param.set_param('bi_website_add_product.surcharge_product', surcharge_product)

    @api.constrains('holiday_surcharge', 'end_date', 'start_date', 'choose_price', 'percentage', 'amount')
    def end_date_checking(self):
        if self.holiday_surcharge is True:
            if not self.start_date:
                raise ValidationError(
                    _("Please choose start date"))
            if not self.end_date:
                raise ValidationError(
                    _("Please choose end date"))
            if self.start_date > self.end_date:
                raise ValidationError(
                    _("End date must be greater than the start date"))
            if (self.end_date - self.start_date).days >= 365:
                raise ValidationError(
                    _("Maximum available period is 1 year."))
            if not self.choose_price:
                raise ValidationError(
                    _("Please choose a price method"))
            if self.choose_price == 'percentage':
                if self.percentage <= 0:
                    raise ValidationError(
                        _("Percentage value must be greater than 0"))
            if self.choose_price == 'amount':
                if self.amount <= 0:
                    raise ValidationError(
                        _("Amount value must be greater than 0"))


    @api.onchange('holiday_surcharge', 'amount', 'choose_price')
    def unselect_product_surcharge(self):
        if self.holiday_surcharge == True:
            surcharge_product = self.env['product.template'].search([('name', '=', "Holiday surcharge")])
            if surcharge_product:
                surcharge_product.write({"available_in_pos": True})
        if self.holiday_surcharge == False:
            surcharge_product = self.env['product.template'].search([('name', '=', "Holiday surcharge")])
            if surcharge_product:
                surcharge_product.write({"available_in_pos": False})
        if self.amount:
            surcharge_product = self.env['product.template'].search([('name', '=', "Holiday surcharge")])
            if surcharge_product:
                surcharge_product.write({"list_price": self.amount})

        if self.choose_price == 'percentage':
            self.amount = 0
        if self.choose_price == 'amount':
            self.percentage = 0


