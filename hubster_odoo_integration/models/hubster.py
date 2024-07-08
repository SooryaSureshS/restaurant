# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import requests
import base64
from odoo.addons.hubster_odoo_integration.models.api_request import req
from odoo.addons.hubster_odoo_integration.models.api_request import scope_auth
import json
import logging

from datetime import datetime

_logger = logging.getLogger(__name__)

class HubsterIntegrationStore(models.Model):

    """Hubster stores informations"""

    _name = 'hubster.store'
    _orderby = 'hubster_sequence_id'
    _rec_name = 'hubster_sequence_id'
    _description = 'Hubster Store Name'


    name = fields.Char(string='Store Name')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
        default=lambda self: self.env.company.id)
    hubster_id = fields.Integer('Hubster store ID')
    hubster_store_detail = fields.Char('Hubster store Name (Mapped through Hubster)')
    hubster_sequence_id = fields.Char('Name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    active = fields.Boolean(string='Active')

    @api.model
    def create(self, vals):
        if vals.get('hubster_sequence_id', _('New')) == _('New'):
            vals['hubster_sequence_id'] = self.env['ir.sequence'].next_by_code('hubster.store.sequence') or _('New')
        return super(HubsterIntegrationStore, self).create(vals)


class HubsterIntegrationConfig(models.Model):

    """Hubster Configurations """

    _name = 'hubster.config'
    _rec_name = 'name'
    _description = 'Hubster Configuration'

    _HUBSTER_ENDPOINT = 'https://partners-staging.tryhubster.com'

    name = fields.Char('Name', required=True, translate=True)
    description = fields.Char('Description', readonly=True)
    image = fields.Binary('Image')
    client_id = fields.Char('Client id', required=True)
    client_secret = fields.Char('Client Secret', required=True)
    token = fields.Char()
    store_id = fields.Many2one('hubster.store', string='store id')
    hubster_endpoint = fields.Char('Hubster EndPoint')


    def action_activate(self):
        if self.client_id and self.client_secret and self.store_id.name:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
                'scope': 'ping',
            }
            try:
                req = requests.post(self.hubster_endpoint+"/v1/auth/token", data=data, headers=headers)
                self.token = req.json().get('access_token');
            except:
                raise ValidationError(_("Please Check the Parameters."))
        else:
            raise ValidationError(_("Please set client id,secret and store."))

    def action_activate_sync(self):
        self.read_huster_menu();
        print("sync",self);


    def read_huster_menu(self):

        """Read hubster Menu"""

        print("menu read")
        client_id = '735c2965-d331-4d07-ae5c-3c84f1452ad5'
        client_id = '735c2965-d331-4d07-ae5c-3c84f1452ad5'
        secret = 'hG~b5KXB~ZIQ~kxwOp.uDpu0ES'
        store_id = 'HUB_STORE_1'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer %s' % self.token,
            'X-Application-Id': self.client_id,
            'X-Store-Id': 'HUB_STORE_1',
            'scope': 'menus.read',
        }
        data = {
            'client_id': client_id,
            'client_secret': secret,
            'grant_type': 'client_credentials',
            'scope': 'menus.read',
        }

        print("header",headers)
        request = requests.get("https://partners-staging.tryhubster.com/v1/menus", data=data, headers=headers)
        print("menus views",request.json())

    def action_check(self):
        headers = {
            'Authorization': 'Bearer %s' % self.token,
            'X-Application-Id': self.client_id,
            'X-Store-Id': self.store_id.name,
        }
        try:
            resp = requests.get(self.hubster_endpoint+"/v1/ping", headers=headers)
            if resp.status_code == 401:
                raise ValidationError(_("Given Credentials is incorrect, please provide correct Credentials."))
            if resp.status_code == 404:
                raise ValidationError(_("please provide correct Endpoints."))
            if resp.status_code == 200:
                raise ValidationError(_("Connection Ok."))
        except:
            raise ValidationError(_("Please Check the Parameters."))

from odoo import api, fields, models, tools, _

class HubsterIntegrationMenus(models.Model):

    """Hubster Menu"""

    _name = 'hubster.menu'
    _rec_name = 'name'
    _description = 'Hubster Menu'

    name = fields.Char('Name', required=True, translate=True)
    description = fields.Char('Description', readonly=True)
    image = fields.Binary('Image')
    fulfillmentModes = fields.Char('fulfillmentModes', default='DELIVERY')
    hubster_id = fields.Integer(default=1)
    category_line = fields.Many2many('product.public.category', string="Category")
    hours_line = fields.One2many('hubster.hours', 'hubster_hour', string="Hours")
    configuration = fields.Many2one('hubster.config', string="Api Configuration")
    status = fields.Char('Status')
    job_ref = fields.Char('Job Reference')
    upsert_token = fields.Char('Upsert Token')

    def action_publish(self):
        try:
            token = scope_auth(self.configuration.hubster_endpoint,method='POST',data=None,secret=self.configuration.client_secret,client_id=self.configuration.client_id,scope='menus.upsert')
            if token.status_code == 200:
                self.write({
                    'upsert_token': token.json().get('access_token'),
                })
                self.env.cr.commit()
                print("json",token.json())
                self.dict_parser(token.json().get('access_token'))
        except Exception as e:
            raise ValidationError(_("Api Response. %s",e))

    def check_connection(self):
        client_id = self.configuration.client_id
        secret = self.configuration.client_secret
        store_id = self.configuration.store_id.name
        token = self.configuration.token

        headers = {
            'Authorization': 'Bearer %s' % token,
            'X-Application-Id': client_id,
            'X-Store-Id': store_id,
        }
        try:
            resp = requests.get(self.configuration.hubster_endpoint + "/v1/ping", headers=headers)
            if resp.status_code == 401:
                raise ValidationError(_("Given Credentials is incorrect, please provide correct Credentials."))
            if resp.status_code == 404:
                raise ValidationError(_("please provide correct Endpoints."))
            if resp.status_code == 200:
                raise ValidationError(_("Connection Ok."))
        except:
            raise ValidationError(_("Please Check the Parameters."))


    def dict_parser(self, token_pass):
        for i in self:
            categoryIds = []
            intervals = []
            item = []
            items = {}
            categories = {}
            modifierGroups = {}

            for cate in i.category_line:
                product_product = self.env['product.template'].search([('public_categ_ids','=', cate.id),('publish_hubster','=',True), ('is_published', '=', True)])
                if not product_product:
                    continue
                categoryIds.append(str(cate.id))

                itemIds = []
                for pro in product_product:
                    if pro.publish_hubster:
                        modifierGroupIds= []
                        # if pro.product_option_group:
                        #     modifierGroupIds.append(str(pro.product_option_group.id))

                        if pro.optional_product_ids:
                            #modifer groups
                            optionalGroups = pro.optional_product_ids.mapped('product_option_group')
                            for opt in optionalGroups:
                                id = str(opt.id)+'-'+str(pro.id)
                                modifierGroups[id] = {
                                    "name": opt.name,
                                    "minimumSelections": opt.min_count,
                                    "maximumSelections": opt.max_count or 1,
                                    "maxPerModifierSelectionQuantity": opt.max_count,
                                    "itemIds": [k.id for k in pro.optional_product_ids if k.product_option_group.id==opt.id],
                                    "id": id
                                }
                                modifierGroupIds.append(id)

                            for opt in pro.optional_product_ids:
                                # if pro.product_option_group:
                                #     modifierGroupIds.append(str(pro.product_option_group.id))
                                opt_pro = {
                                    "name": opt.name,
                                    "description": '',
                                    "modifierGroupIds": [],
                                    "status": {
                                        "saleStatus": "FOR_SALE"
                                    },
                                    "price": {
                                        "currencyCode": self.env.ref('base.main_company').currency_id.name,
                                        "amount": opt.list_price
                                    },
                                    "id": opt.id
                                }
                                items[opt.id] = opt_pro
                                # itemIds.append(opt.id)
                        p = {
                            "name": pro.name,
                            "description": pro.description_sale if pro.description_sale else '',
                            "modifierGroupIds": modifierGroupIds,
                            "status": {
                                "saleStatus": "FOR_SALE"
                            },
                            "price": {
                                "currencyCode": self.env.ref('base.main_company').currency_id.name,
                                "amount": pro.list_price
                            },
                            "id": pro.id
                        }
                        items[pro.id] = p
                        itemIds.append(pro.id)
                c = {
                    "name": cate.name,
                    "description": "",
                    "itemIds": itemIds,
                    "id": cate.id
                }
                categories[cate.id] = c

            for inter in i.hours_line:
                d = {
                      "day": inter.day,
                      "fromHour": inter.fromHour,
                      "fromMinute": inter.fromMinute,
                      "toHour": inter.toHour,
                      "toMinute": inter.toMinute
                    }
                intervals.append(d)
            dict = {
                "menus": {
                    self.id : {
                        "name": self.name,
                        "categoryIds": categoryIds,
                        "fulfillmentModes": ["DELIVERY"],
                        "id": self.id,
                        "description": self.description if self.description else '',
                        "hours": {
                            "intervals": intervals,
                        }
                    }
                },

                "items": items,
                "categories": categories,
                "modifierGroups": modifierGroups
            }


        if dict and self.configuration.client_id and self.configuration.store_id.name:
            headers = {
                'Authorization': 'Bearer %s' %token_pass,
                'X-Application-Id': self.configuration.client_id,
                'X-Store-Id': self.configuration.store_id.name,
                'Content-Type': 'application/json',
                'scope': 'menus.upsert',
            }
            request = requests.post(self.configuration.hubster_endpoint+"/v1/menus", data=json.dumps(dict), headers=headers)
            self.env.cr.execute(""" INSERT INTO hubster_payloads(name,payloads,payloads_date) VALUES(%s,%s,%s)""",
                                [str(self.name), str(dict), str(datetime.now()), ])
            if request.status_code == 202:
                dict = request.json()
                job_ref = dict['jobReference']
                self.write({
                    'status': job_ref.get('status'),
                    'job_ref': job_ref['id'],
                })
                self.env.cr.commit()

                raise ValidationError(_("job id is %s and Status %s",job_ref['id'],job_ref['status']))
            else:
                raise ValidationError(_("We can't pass empty product inside product Category."))


    def webhook_event_trigger(self):
        print("webhook event trigger to server",self)


class HubsterIntegrationMenuHours(models.Model):

    """Hubster Menu Hours ;
        description: used to feed available Time for a store
    """

    _name = 'hubster.hours'
    _rec_name = 'name'
    _description = 'Hubster Menu'


    name = fields.Char('Name', required=True, translate=True)
    day = fields.Selection(
        [('MONDAY', 'MONDAY'),
         ('SATURDAY', 'SATURDAY'),
         ('TUESDAY', 'TUESDAY'),
         ('THURSDAY', 'THURSDAY'),
         ('WEDNESDAY', 'WEDNESDAY'),
         ('FRIDAY', 'FRIDAY'),
         ('SUNDAY', 'SUNDAY'),
         ],
        'day', required=True)

    fromHour = fields.Integer(default=0)
    fromMinute = fields.Integer(default=0)
    toHour = fields.Integer(default=23)
    toMinute = fields.Integer(default=59)
    hubster_hour = fields.Many2one('hubster.menu')




class HubsterIntegrationCategory(models.Model):

    _inherit = 'pos.category'

    hubster_menu = fields.Many2one('hubster.menu', string="Home offers")


class HubsterIntegrationCategoryTemplate(models.Model):

    _inherit = 'product.template'

    publish_hubster = fields.Boolean('Hubster Enable')

class HubsterOrderModel(models.Model):

    _name = 'hubster.order'
    _rec_name = 'name'
    _description = 'Hubster Order'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    event_id = fields.Char()
    event_time = fields.Char()
    event_type = fields.Char()
    source = fields.Char()
    external_identifiers = fields.Char()
    friendly_id = fields.Char()
    ordered_at = fields.Char()
    currency_code = fields.Char()
    customer = fields.Char()
    partner = fields.Many2one('res.partner')
    customer_note = fields.Char()
    status = fields.Char()
    delivery_info = fields.Char()
    source_document = fields.Many2one('sale.order', readonly=True)
    order_line = fields.One2many('hubster.order.line', 'orders')
    subtotal = fields.Float('subtotal')
    discount = fields.Float('discount')
    tax = fields.Float('tax')
    deliveryFee = fields.Float('deliveryFee')
    total = fields.Float('total')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hubster.order.sequence') or _('New')
        return super(HubsterOrderModel, self).create(vals)

class HubsterOrderModelnew(models.Model):

    _name = 'hubster.order.line'
    _rec_name = 'name'

    orders = fields.Many2one('hubster.order')
    sku_price = fields.Float()
    product_template_id = fields.Many2one('product.template')
    product_id = fields.Many2one('product.product')
    name = fields.Char()
    qty = fields.Float()
    note = fields.Char()
    category = fields.Many2one('pos.category')
    base_price = fields.Float()



class HubsterIntegrationSaleOrder(models.Model):

    _inherit = 'sale.order'

    friendly_id = fields.Char()
    is_hubster = fields.Boolean()


class hubsterPayloads(models.Model):

    _name = 'hubster.payloads'

    name = fields.Char('Menu')
    payloads = fields.Char('Payload')
    payloads_date = fields.Char('Payload date')


