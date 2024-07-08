from odoo import fields, models


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    visible_group_ids = fields.Many2many('res.groups', 'visible_group', string='Visible For Groups')

    def menu_visibility(self, user):
        visible_group_ids = self.visible_group_ids.ids
        if visible_group_ids:
            for group_id in visible_group_ids:
                if group_id in user.groups_id.ids:
                    return True
            return False
        else:
            return True



class WebsiteUrl(models.Model):
    _name = 'website.url'
    _rec_name = 'url'

    url = fields.Char()


class Website(models.Model):
    _inherit = 'website'

    private_urls = fields.Many2many('website.url', 'private_url')

