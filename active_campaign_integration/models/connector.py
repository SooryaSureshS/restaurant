# # -*- coding: utf-8 -*-
#
# import base64
# import datetime
# import json
# import re
# import requests
# from odoo.exceptions import ValidationError
# from odoo import api, fields, models, _
# from odoo.exceptions import Warning
# from werkzeug import urls
# from activecampaign.client import Client
#
#
# class CredentialUrl(models.Model):
#     _name = 'active.campaign'
#     _description = 'Active Campaign'
#
#     name = fields.Char(string='App Name', required=True)
#     clienturl = fields.Char(string='URL', required=True)
#     clientkey = fields.Char(string='Key', required=True)
#     active = fields.Boolean(string='Active', default=True)
#     account_id = fields.Char(default=1, invisible=True)
#     company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
#     order_field_id = fields.Char(string='Order Field Id', store=True)
#     product_field_id = fields.Char(string='Product Field Id', store=True)
#     total_amount_field_id = fields.Char(string='Total Amount Field Id', store=True)
#
#     def authorize_and_get_token(self):
#         self.ensure_one()
#         client = Client(self.clienturl, self.clientkey)
#         response = client.contacts.list_all_contacts()
#         if response:
#             raise ValidationError(
#                 _("Connection Successful"))
#         else:
#             raise ValidationError(
#                 _("Connection failed"))
#
#     def get_contact(self):
#         self.ensure_one()
#         client = Client(self.clienturl, self.clientkey)
#         response = client.contacts.list_all_contacts()
#
#     def create_contact(self, record):
#         active_camp = self.env['active.campaign'].search([])
#         active_partner = self.env['res.partner'].search([('email', '=', record.get('email'))])
#         if record.get('function'):
#             title = record.get('function')
#         else:
#             title = " "
#         data = {
#             "contact": {
#                 "email": record.get('email'),
#                 "firstName": record.get('name'),
#                 "lastName": " ",
#                 "phone": record.get('phone'),
#             }
#         }
#         client = Client(active_camp.clienturl, active_camp.clientkey)
#         response = client.contacts.create_a_contact(data)
#         if response.get('contact'):
#             active_camp_partner = self.env['res.partner'].search([('email', '=', record.get('email'))])
#             active_camp_partner.write({'active_campaign_contact_id': response.get('contact').get('id')})
#             headers = {
#                 'Api-Token': active_camp.clientkey,
#                 'Accept': "application/json",
#                 'Content-Type': "application/json",
#             }
#             data = json.dumps({
#                 "accountContact": {
#                     "account": active_camp.account_id,
#                     "contact": response.get('contact').get('id'),
#                     "jobTitle": title
#                 }
#             })
#             url = active_camp.clienturl + "/api/3/accountContacts"
#             response = requests.post(url, headers=headers, data=data)
#             res = json.loads(response.text)
#             if res.get('accountContact'):
#                 active_camp_partner.write({'active_campaign_association_id': res.get('accountContact').get('id')})
#
#             for tag in active_camp_partner.category_id:
#                 if tag.active_campaign_tag_id:
#
#                     data = {
#                         "contactTag": {
#                             "contact": active_camp_partner.active_campaign_contact_id,
#                             "tag": tag.active_campaign_tag_id
#                         }
#                     }
#                     response = client.contacts.add_a_tag_to_contact(data)
#                 else:
#                     self.create_tags(tag)
#                     tag = self.env['res.partner.category'].search([('id', '=', tag.id)])
#                     data = {
#                         "contactTag": {
#                             "contact": active_camp_partner.active_campaign_contact_id,
#                             "tag": tag.active_campaign_tag_id
#                         }
#                     }
#                     response = client.contacts.add_a_tag_to_contact(data)
#         else:
#             pass
#             # raise ValidationError(
#             #     _(response))
#
#     def update_contact(self, record, changed_data):
#         active_camp = self.env['active.campaign'].search([])
#         active_partner = self.env['res.partner'].search([('id', '=', record._origin.id)])
#         if active_partner and active_partner.active_campaign_contact_id:
#             active_camp = self.env['active.campaign'].search([])
#             data = {
#                 "contact": changed_data
#
#             }
#             client = Client(active_camp.clienturl, active_camp.clientkey)
#             response = client.contacts.update_a_contact(active_partner.active_campaign_contact_id, data)
#
#     def delete_contact(self, record):
#         active_camp = self.env['active.campaign'].search([])
#         active_partner = self.env['res.partner'].search([('id', '=', record._origin.id)])
#         if active_partner and active_partner.active_campaign_contact_id:
#             client = Client(active_camp.clienturl, active_camp.clientkey)
#             response = client.contacts.delete_a_contact(active_partner.active_campaign_contact_id)
#
#     def update_contact_job_title(self, record,job):
#         active_camp = self.env['active.campaign'].search([])
#         active_partner = self.env['res.partner'].search([('id', '=', record._origin.id)])
#         if active_partner and active_partner.active_campaign_contact_id:
#             headers = {
#                 'Api-Token': active_camp.clientkey,
#                 'Accept': "application/json",
#                 'Content-Type': "application/json",
#             }
#             data = json.dumps({
#                 "accountContact": {
#                     "jobTitle": job
#                 }
#             })
#             url = active_camp.clienturl + "/api/3/accountContacts/" + active_partner.active_campaign_association_id
#             response = requests.put(url, headers=headers, data=data)
#
#     def create_tags(self, record):
#         active_camp = self.env['active.campaign'].search([])
#         client = Client(active_camp.clienturl, active_camp.clientkey)
#         tag = self.env['res.partner.category'].search([('id', '=', record.id)])
#
#         data = {
#             "tag": {
#                 "tag": tag.name,
#                 "tagType": "contact",
#                 "description": ""
#             }
#         }
#
#         response = client.tags.create_a_tag(data)
#         if response.get('tag'):
#             active_camp = self.env['res.partner.category'].search([('name', '=', record['name'])])
#             active_camp.write({'active_campaign_tag_id': response.get('tag').get('id')})
#
#     def create_new_tags(self, record):
#         active_camp = self.env['active.campaign'].search([])
#         client = Client(active_camp.clienturl, active_camp.clientkey)
#
#         data = {
#             "tag": {
#                 "tag": record['name'],
#                 "tagType": "contact",
#                 "description": ""
#             }
#         }
#
#         response = client.tags.create_a_tag(data)
#         if response.get('tag'):
#             active_camp = self.env['res.partner.category'].search([('name', '=', record['name'])])
#             active_camp.write({'active_campaign_tag_id': response.get('tag').get('id')})
#
#     def update_order_data(self, record, changed_data):
#         sale_order = self.env['sale.order'].search([('name', '=', changed_data['orderId'])])
#         active_partner = self.env['res.partner'].search([('id', '=', sale_order.partner_id.id)])
#         if active_partner and active_partner.active_campaign_contact_id and active_partner.type != 'delivery':
#             active_camp = self.env['active.campaign'].search([])
#             url = active_camp.clienturl + "/api/3/fieldValues"
#             headers = {
#                 'Api-Token': active_camp.clientkey,
#                 'Accept': "application/json",
#                 'Content-Type': "application/json",
#             }
#             client = Client(active_camp.clienturl, active_camp.clientkey)
#             response = requests.get(url, headers=headers)
#             res = json.loads(response.text)
#             field_values = res.get('fieldValues')
#             if not field_values:
#                 active_camp = self.env['active.campaign'].search([])
#                 url = active_camp.clienturl + "/api/3/fields"
#                 data = json.dumps(
#                     {
#
#                         "field": {
#                             "type": "text",
#                             "title": "Order Id",
#                             "descript": "",
#                             "isrequired": 0,
#                             "perstag": "ORDER ID",
#                             "defval": 0,
#                             "visible": 1,
#                             "ordernum": 1
#                         }
#                     })
#                 headers = {
#                     'Api-Token': active_camp.clientkey,
#                     'Accept': "application/json",
#                     'Content-Type': "application/json",
#                 }
#                 client = Client(active_camp.clienturl, active_camp.clientkey)
#                 response = requests.post(url, headers=headers, data=data)
#                 res = json.loads(response.text)
#                 active_camp.write({'order_field_id': res.get('field').get('id')})
#
#                 res = json.loads(response.text)
#                 active_camp = self.env['active.campaign'].search([])
#                 url = active_camp.clienturl + "/api/3/fields"
#                 data = json.dumps(
#                     {
#
#                         "field": {
#                             "type": "textarea",
#                             "title": "Products",
#                             "descript": "",
#                             "isrequired": 0,
#                             "perstag": "PRODUCTS",
#                             "defval": 0,
#                             "visible": 1,
#                             "ordernum": 2
#                         }
#                     })
#                 headers = {
#                     'Api-Token': active_camp.clientkey,
#                     'Accept': "application/json",
#                     'Content-Type': "application/json",
#                 }
#                 client = Client(active_camp.clienturl, active_camp.clientkey)
#                 response = requests.post(url, headers=headers, data=data)
#                 res = json.loads(response.text)
#                 active_camp.write({'product_field_id': res.get('field').get('id')})
#                 res = json.loads(response.text)
#                 active_camp = self.env['active.campaign'].search([])
#                 url = active_camp.clienturl + "/api/3/fields"
#                 data = json.dumps(
#                     {
#
#                         "field": {
#                             "type": "text",
#                             "title": "Total Amount",
#                             "descript": "",
#                             "isrequired": 0,
#                             "perstag": "TOTAL AMOUNT",
#                             "defval": 0,
#                             "visible": 1,
#                             "ordernum": 3
#                         }
#                     })
#                 headers = {
#                     'Api-Token': active_camp.clientkey,
#                     'Accept': "application/json",
#                     'Content-Type': "application/json",
#                 }
#                 client = Client(active_camp.clienturl, active_camp.clientkey)
#                 response = requests.post(url, headers=headers, data=data)
#                 res = json.loads(response.text)
#                 active_camp.write({'total_amount_field_id': res.get('field').get('id')})
#
#             data = json.dumps(
#                 {
#                     "fieldValue": {
#                         "contact": active_partner.active_campaign_contact_id,
#                         "field": active_camp.order_field_id,
#                         "value": changed_data['orderId']
#                     },
#
#                 }
#             )
#             url = active_camp.clienturl + "/api/3/fieldValues"
#
#             client = Client(active_camp.clienturl, active_camp.clientkey)
#             response = requests.post(url, headers=headers, data=data)
#             res = json.loads(response.text)
#
#             s = ","
#             for i in changed_data['productName']:
#                 data = json.dumps(
#                     {
#                         "fieldValue": {
#                             "contact": active_partner.active_campaign_contact_id,
#                             "field": active_camp.product_field_id,
#                             "value": s.join(changed_data['productName'])
#                         },
#
#                     }
#                 )
#             url = active_camp.clienturl + "/api/3/fieldValues"
#             client = Client(active_camp.clienturl, active_camp.clientkey)
#             response = requests.post(url, headers=headers, data=data)
#             res = json.loads(response.text)
#             data = json.dumps(
#                 {
#                     "fieldValue": {
#                         "contact": active_partner.active_campaign_contact_id,
#                         "field": active_camp.total_amount_field_id,
#                         "value": changed_data['totalAmount']
#                     },
#
#                 }
#             )
#
#             url = active_camp.clienturl + "/api/3/fieldValues"
#
#             client = Client(active_camp.clienturl, active_camp.clientkey)
#             response = requests.post(url, headers=headers, data=data)
#             res = json.loads(response.text)
#         else:
#             sale_order = self.env['sale.order'].search([('name', '=', changed_data['orderId'])])
#             active_partner = self.env['res.partner'].search([('id', '=', sale_order.partner_id.id)])
#             if active_partner:
#                 vals_list = {
#                     "email": active_partner.email,
#                     "name": active_partner.name,
#                     "lastName": " ",
#                     "phone": active_partner.phone,
#                 }
#
#                 self.env['active.campaign'].create_contact(vals_list)
#                 contact_id = self.env['active.campaign'].create_contact(vals_list)
#                 sale_order = self.env['sale.order'].search([('name', '=', changed_data['orderId'])])
#                 active_partner = self.env['res.partner'].search([('id', '=', sale_order.partner_id.id)])
#                 if active_partner and active_partner.active_campaign_contact_id:
#                     active_camp = self.env['active.campaign'].search([])
#                     url = active_camp.clienturl + "/api/3/fieldValues"
#                     headers = {
#                         'Api-Token': active_camp.clientkey,
#                         'Accept': "application/json",
#                         'Content-Type': "application/json",
#                     }
#                     client = Client(active_camp.clienturl, active_camp.clientkey)
#                     response = requests.get(url, headers=headers)
#                     res = json.loads(response.text)
#                     field_values = res.get('fieldValues')
#                     if not field_values:
#                         active_camp = self.env['active.campaign'].search([])
#                         url = active_camp.clienturl + "/api/3/fields"
#                         data = json.dumps(
#                             {
#
#                                 "field": {
#                                     "type": "text",
#                                     "title": "Order Id",
#                                     "descript": "",
#                                     "isrequired": 0,
#                                     "perstag": "ORDER ID",
#                                     "defval": 0,
#                                     "visible": 1,
#                                     "ordernum": 1
#                                 }
#                             })
#                         headers = {
#                             'Api-Token': active_camp.clientkey,
#                             'Accept': "application/json",
#                             'Content-Type': "application/json",
#                         }
#                         client = Client(active_camp.clienturl, active_camp.clientkey)
#                         response = requests.post(url, headers=headers, data=data)
#                         res = json.loads(response.text)
#                         active_camp.write({'order_field_id': res.get('field').get('id')})
#                         res = json.loads(response.text)
#                         active_camp = self.env['active.campaign'].search([])
#                         url = active_camp.clienturl + "/api/3/fields"
#                         data = json.dumps(
#                             {
#
#                                 "field": {
#                                     "type": "textarea",
#                                     "title": "Products",
#                                     "descript": "",
#                                     "isrequired": 0,
#                                     "perstag": "PRODUCTS",
#                                     "defval": 0,
#                                     "visible": 1,
#                                     "ordernum": 2
#                                 }
#                             })
#                         headers = {
#                             'Api-Token': active_camp.clientkey,
#                             'Accept': "application/json",
#                             'Content-Type': "application/json",
#                         }
#                         client = Client(active_camp.clienturl, active_camp.clientkey)
#                         response = requests.post(url, headers=headers, data=data)
#                         res = json.loads(response.text)
#                         active_camp.write({'product_field_id': res.get('field').get('id')})
#                         res = json.loads(response.text)
#                         active_camp = self.env['active.campaign'].search([])
#                         url = active_camp.clienturl + "/api/3/fields"
#                         data = json.dumps(
#                             {
#
#                                 "field": {
#                                     "type": "text",
#                                     "title": "Total Amount",
#                                     "descript": "",
#                                     "isrequired": 0,
#                                     "perstag": "TOTAL AMOUNT",
#                                     "defval": 0,
#                                     "visible": 1,
#                                     "ordernum": 3
#                                 }
#                             })
#                         headers = {
#                             'Api-Token': active_camp.clientkey,
#                             'Accept': "application/json",
#                             'Content-Type': "application/json",
#                         }
#                         client = Client(active_camp.clienturl, active_camp.clientkey)
#                         response = requests.post(url, headers=headers, data=data)
#                         res = json.loads(response.text)
#                         active_camp.write({'total_amount_field_id': res.get('field').get('id')})
#
#                     data = json.dumps(
#                         {
#                             "fieldValue": {
#                                 "contact": active_partner.active_campaign_contact_id,
#                                 "field": active_camp.order_field_id,
#                                 "value": changed_data['orderId']
#                             },
#
#                         }
#                     )
#
#                     url = active_camp.clienturl + "/api/3/fieldValues"
#                     client = Client(active_camp.clienturl, active_camp.clientkey)
#                     response = requests.post(url, headers=headers, data=data)
#                     res = json.loads(response.text)
#                     s = ","
#                     for i in changed_data['productName']:
#                         data = json.dumps(
#                             {
#                                 "fieldValue": {
#                                     "contact": active_partner.active_campaign_contact_id,
#                                     "field": active_camp.product_field_id,
#                                     "value": s.join(changed_data['productName'])
#                                 },
#
#                             }
#                         )
#
#                     url = active_camp.clienturl + "/api/3/fieldValues"
#                     client = Client(active_camp.clienturl, active_camp.clientkey)
#                     response = requests.post(url, headers=headers, data=data)
#                     res = json.loads(response.text)
#                     data = json.dumps(
#                         {
#                             "fieldValue": {
#                                 "contact": active_partner.active_campaign_contact_id,
#                                 "field": active_camp.total_amount_field_id,
#                                 "value": changed_data['totalAmount']
#                             },
#
#                         }
#                     )
#
#                     url = active_camp.clienturl + "/api/3/fieldValues"
#                     client = Client(active_camp.clienturl, active_camp.clientkey)
#                     response = requests.post(url, headers=headers, data=data)
#                     res = json.loads(response.text)
#
