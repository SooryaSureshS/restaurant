# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import functools
import json
import logging
import math
import re
import passlib.context

from werkzeug import urls

from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
from odoo.addons.portal.controllers import portal
import odoo
import threading
from dateutil.relativedelta import relativedelta
from odoo.tools import html_escape
from passlib.context import CryptContext
from hashlib import sha256

def get_db_name():
    db = odoo.tools.config['db_name']
    if not db and hasattr(threading.current_thread(), 'dbname'):
        return threading.current_thread().dbname
    return db

class CustomerPortalInhrited(portal.CustomerPortal):

    @route(['/my', '/my/home'], type='http', auth="public", website=True)
    def home(self, **kw):
        values = super(CustomerPortalInhrited, self).home(**kw)
        uid = request.env.user.id
        if uid:
            if uid == 4:
                return request.render("mask_cutomization.skypro_my_home_no_login")
            else:
                partner = request.env['res.users'].sudo().search([('id', '=', int(uid))], limit=1)
                if not request.session.get('edit_partner'):
                    request.session['edit_partner'] = partner.partner_id[0].id
                return request.render("mask_cutomization.skypro_my_home")

    @route(['/portal/information'], type='json', auth="user", website=True)
    def portalInformation(self, **kw):
        uid = request.env.user.id
        obj = request.env['res.users'].sudo().search([('id','=',int(uid))],limit=1)
        return obj

    @route(['/portal/session/save'], type='json', auth="user", website=True)
    def portalSessionSave(self, address=None, type=None, **kw):
        request.session['edit_partner'] = address
        request.session['billing'] = type
        return request.session['edit_partner']

    @http.route('/edit/partner/info', website=True, auth='public')
    def editPartnerInfo(self,  **kw):
        dict = {}

        if kw.get('name'):
            dict['first_name'] = kw.get('name') or False
            dict['name'] = kw.get('name') or False
        if kw.get('last_name'):
            dict['last_name']: kw.get('last_name') or False
        if kw.get('phone_code'):
            dict['phone_code'] = kw.get('phone_code') or False
        if kw.get('phone'):
            dict['phone'] = kw.get('phone') or False
        if kw.get('email'):
            dict['email'] = kw.get('email') or False
        if kw.get('company_name'):
            dict['company_name'] = kw.get('company_name') or False
        if kw.get('country_id'):
            dict['country_id'] = int(kw.get('country_id')) or False
        if kw.get('street'):
            dict['street'] = kw.get('street') or False
        if kw.get('street2'):
            dict['street2'] = kw.get('street2') or False
        if kw.get('mode_type') == '0':
            if kw.get('partner_id'):
                partner = request.env['res.partner'].sudo().search([('id','=',kw.get('partner_id'))], limit=1)
                # kw.update({'active': True})
                kw.pop('partner_id')
                kw.pop('phone')
                a = partner.sudo().write(dict)
        else:
            if request.session['billing'] == 'billing':
                uid = request.env.user.id
                user = request.env['res.users'].sudo().search([('id','=',uid)], limit=1)
                dict['parent_id'] = user.partner_id.id
                dict['type'] = 'invoice'
                request.env['res.partner'].sudo().create(dict)
            if request.session['billing'] == 'delivery':
                uid = request.env.user.id
                user = request.env['res.users'].sudo().search([('id','=',uid)], limit=1)
                dict['parent_id'] = user.partner_id.id
                dict['type'] = 'delivery'
                request.env['res.partner'].sudo().create(dict)

        return request.redirect('/my')

    @route(['/res/country/read'], type='json', auth="none", website=True)
    def resCountryRead(self, country=None, **kw):
        states = request.env['res.country.state'].sudo().search([('country_id','=',int(country))])
        li = []
        for state in states:
            di = {
                'id': state.id,
                'name': state.name,
                'code': state.code,
            }
            li.append(di)
        return li




    @route(['/forgot/password/user'], type='json', auth="public", website=True)
    def forgotPassword(self, old_pass=None,new_pass=None,new_confirm=None, **kw):
        print("info",old_pass,new_pass,new_confirm)
        data = request.httprequest.data
        uid = request.env.user.id
        user = request.env['res.users'].sudo().search([('id', '=', int(uid))], limit=1)
        data = json.loads(data)
        db = get_db_name()
        error_code = False
        try:
            if new_pass == new_confirm:
                auth = request.session.authenticate(db, user.login,old_pass)
                ctx = passlib.context.CryptContext(
                    ['pbkdf2_sha512', 'plaintext'],
                    deprecated=['plaintext'],
                )
                if user:
                    hash_password = ctx.hash if hasattr(ctx, 'hash') else ctx.encrypt
                    user._set_encrypted_password(user.id, hash_password(new_confirm))
                    return {'success': True, 'message': "New Password has been reset"}
            else:
                return {
                    'error_code': "new password and confirm password are not same",
                    'success': False
                }
        except Exception as e:
            error_code = e
        return {
            'error_code': error_code,
            'success': False
        }

    @route(['/my/order/process'], type='http', auth="public", website=True)
    def orderProcessPage(self, **kw):
        return request.render("mask_cutomization.order_process_page")

    @route(['/payment/delivery'], type='http', auth="public", website=True)
    def orderPaymentDelivery(self, **kw):

        return request.render("mask_cutomization.payment_and_delivery_page")

    @route(['/privacy/policy'], type='http', auth="public", website=True)
    def orderPrivacyPolicy(self, **kw):

        return request.render("mask_cutomization.privacy_policy_page")

    @route(['/notification/changed'], type='json', auth="public", website=True)
    def notificationChanges(self, state=None, **kw):
        uid = request.env.user.id
        user = request.env['res.users'].sudo().search([('id', '=', int(uid))], limit=1)
        if state == 'on':
            if user:
                user.sudo().write({
                    'enable_token' : True
                })
            # request.env['ir.config_parameter'].sudo().set_param('firebase_push_notification.enable', True)
        else:
            if user:
                user.sudo().write({
                    'enable_token' : False
                })
            # request.env['ir.config_parameter'].sudo().set_param('firebase_push_notification.enable', False)
        return True