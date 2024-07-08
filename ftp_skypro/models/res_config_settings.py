from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_ftp = fields.Boolean('Use FTP')
    ftp_ip_address = fields.Char('IP Address')
    ftp_user_name = fields.Char(string="User Name")
    ftp_password = fields.Char(string="Password")
    ftp_xml_directory = fields.Char(string="XML File Directory")
    ftp_image_directory = fields.Char(string="Image Directory")
    product_pack_image = fields.Binary(string="Package Image")
    product_carton_image = fields.Binary(string="Carton Image")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(use_ftp=self.env['ir.config_parameter'].sudo().get_param('ftp_skypro.use_ftp'))
        res.update(ftp_ip_address=self.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_ip_address'))
        res.update(ftp_user_name=self.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_user_name'))
        res.update(ftp_password=self.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_password'))
        res.update(ftp_xml_directory=self.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_xml_directory'))
        res.update(ftp_image_directory=self.env['ir.config_parameter'].sudo().get_param('ftp_skypro.ftp_image_directory'))
        res.update(product_pack_image=self.env['ir.config_parameter'].sudo().get_param('ftp_skypro.product_pack_image'))
        res.update(product_carton_image=self.env['ir.config_parameter'].sudo().get_param('ftp_skypro.product_carton_image'))
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('ftp_skypro.use_ftp', self.use_ftp)
        param.set_param('ftp_skypro.ftp_ip_address', self.ftp_ip_address)
        param.set_param('ftp_skypro.ftp_user_name', self.ftp_user_name)
        param.set_param('ftp_skypro.ftp_password', self.ftp_password)
        param.set_param('ftp_skypro.ftp_image_directory', self.ftp_image_directory)
        param.set_param('ftp_skypro.ftp_xml_directory', self.ftp_xml_directory)
        param.set_param('ftp_skypro.product_pack_image', self.product_pack_image)
        param.set_param('ftp_skypro.product_carton_image', self.product_carton_image)
