from odoo.http import Controller, route, request
import pytz

from dateutil.relativedelta import relativedelta
from datetime import timedelta


class OrderFetch(Controller):

    @route('/longpolling/pollings/order/fetch', type="json", auth="public", cors="*", csrf=False)
    def order_fetch(self, session_id):
        po = []
        order_sequence_pos = []
        order_sequence_so = []
        so = []
        sessions = request.env['pos.session'].sudo().search([('id', '=', session_id)], limit=1)
        all_category = request.env['pos.category'].sudo().search([])
        all_category = [{'name':i.name,'id':i.id} for i in all_category]
        user_type = sessions.user_id
        config_id = sessions.config_id
        from datetime import datetime
        from datetime import timedelta
        tz = pytz.timezone(user_type.tz or 'UTC')


        #pos order
        pos_order_line_domain = ['cancel', 'return', 'done']
        domain = [('lines.order_line_state', 'not in', ['cancel', 'done', 'return', False])]
        pos_line = request.env['pos.order'].sudo().search(domain, order='date_order ASC')
        pos_count = 0
        tz = pytz.timezone(user_type.tz or 'UTC')
        for i in pos_line:
            list = []
            optional_line = []
            previous_line = False
            for line in i.lines.filtered(lambda r:  r.order_line_state not in pos_order_line_domain):
                if line.qty > 0 and line.qty - line.returned_qty > 0:
                    data = {
                        'create_date': line.create_date.astimezone(tz),
                        'floor': line.floor,
                        'full_product_name': line.full_product_name,
                        'id': line.id,
                        'name': line.name,
                        'order_line_note': line.order_line_note,
                        'order_line_state': line.order_line_state,
                        'product_uom_qty': line.qty - line.returned_qty,
                        'table': line.table,
                        'pos_categ_id': line.product_id.pos_categ_id.id,
                        'pos_categ_name': line.product_id.pos_categ_id.name,
                        'pos_categ_sequence': line.product_id.pos_categ_id.sequence or 0,
                        'customer': [line.customer.id, line.customer.name] or False,
                        'price_lst': line.product_id.lst_price or False,
                        'price': line.price_subtotal or False,
                        'discount': line.discount or False,
                        'price_display': line.price_subtotal_incl or False,
                        'product_id': line.product_id.id or False,
                        'preparation_time': line.preparation_time or False,
                        'preparation_estimation': line.preparation_date.astimezone(tz) + timedelta(hours=0,
                                                                                                   minutes=line.preparation_time),
                        'is_optional': line.product_id.is_optional_product or False,
                        'website_delivery_type': 'pos_order',
                        'order_line_mark': line.order_line_mark or False,
                        'note': line.note or False,
                        # 'disable_print': line.product_id.disable_print
                    }
                    if line.product_id.is_optional_product:
                        data['parent_line'] = previous_line
                        data['icon'] = line.product_id.product_option_group.icon or False
                        optional_line.append(data)
                    else:
                        previous_line = line.id
                        list.append(data)
            printed = []
            if len(list) > 0:
                t2 = i.date_order.astimezone(tz)
                pos_full_order = {
                    'name': i.name,
                    'partner_contact': i.partner_id.phone if i.partner_id else False,
                    'printed': printed or False,
                    'customer': [i.partner_id.id, i.partner_id.name] or False,
                    'order_id': i.id,
                    'pos_reference': i.pos_reference,
                    'order_time': t2.strftime('%H:%M'),
                    'preparation_time': i.preparation_time,
                    'type': 'pos',
                    'amount_total': i.amount_total,
                    'amount_tax': i.amount_tax,
                    'preparation_date': i.preparation_date.astimezone(tz),
                    'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(hours=0,
                                                                                            minutes=i.preparation_time),
                    'kitchen_screen': i.kitchen_screen,
                    'website_delivery_type': 'pos_order',
                    'table': i.table_name,
                    'delivery_type': i.delivery_type,
                    'pos_order_note': i.note,
                    'delivery_note': i.delivery_note,
                    'date_order': i.date_order,
                    'order_sequence': i.order_sequence,
                    'filter_date': i.date_order,
                    'all_category': all_category,
                    'street': i.partner_id.street if i.partner_id else False,
                    'street2': i.partner_id.street2 if i.partner_id else False,
                    'city': i.partner_id.city if i.partner_id else False,
                    'zip': i.partner_id.zip if i.partner_id else False,
                    'cover': i.table_id.seats if i.table_id else False,
                    'floor': i.table_id.floor_id.name if i.table_id else False,
                    'tables': i.table_id.name if i.table_id else False,
                }
                change_ids =[]
                if i.change_ids:
                    pos_full_order['change_order']= True
                    for change in i.change_ids:
                        change_ids.append({'product':change.product_id.name,'qty':change.qty})
                else:
                    pos_full_order['change_order'] = False
                pos_full_order['change_ids']= change_ids
                sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])

                # print_order_line_all = []
                parent_lines = [i['parent_line'] for i in optional_line if i['parent_line']]
                for pos_cat  in config_id.printer_ids:
                    order_line_data = []
                    product_categories_ids = pos_cat.product_categories_ids.ids
                    for act_line in sorted_order_line:
                        if act_line['pos_categ_id'] in product_categories_ids:
                            pa_line=act_line.copy()
                            # order_line.append(act_line)
                            optional_line_pos =[]
                            for opt in optional_line:
                                if pa_line['id'] == opt['parent_line']:
                                    optional_line_pos.append(opt)
                            pa_line['optional_line_pos']=optional_line_pos
                            order_line_data.append(pa_line)
                    if len(order_line_data)>0:
                        pos_order = pos_full_order.copy()
                        pos_order['is_pass'] =pos_cat.is_pass_printer
                        pos_order['printer_name'] = pos_cat.name
                        pos_order['order_line']= order_line_data
                        ids = []
                        for i in order_line_data:
                            ids.append(i['id'])
                            for k in i['optional_line_pos']:
                                ids.append(k['id'])
                        if bool(ids):
                            orders = request.env['pos.order.line'].sudo().browse(ids)
                            for o in orders:
                                o.write({'order_line_state': 'done'})
                        po.append({pos_cat.id:pos_order})


        #sale order
        sale_domain = False
        search_domain =  [('order_line.order_line_state', 'not in', ['cancel', 'return', 'done']),('state','=','sale'),('parent_id','=',False)]
        if sale_domain!=False:
            search_domain.append(sale_domain)
        so_line = request.env['sale.order'].sudo().search(search_domain, order='date_order ASC')
        current_date_time = datetime.now()

        from datetime import timedelta
        from datetime import datetime

        current_uid = request.env.user
        user_type = request.env['res.users'].sudo().search([('id', '=', current_uid.id)])
        is_cook = user_type.kitchen_screen_user
        # if not sessions.config_id.show_only_pos_order:
        categories_id = request.env.user.pos_category_ids.ids
        for i in so_line:
            list = []
            optional_line = []
            previous_line = False
            if i.state == 'sale':
                t1 = i.date_order.astimezone(tz)
                # if is_cook == "manager" or is_cook=='admin':
                selected_line=False
                for lines in i.order_line.filtered(lambda r: r.order_line_state not in ['cancel', 'return', 'done'] and r.product_id.is_optional_product==False and r.bundle_child == False):
                    if lines:
                        if not selected_line:
                                selected_line = lines
                        if lines.preparation_date_delivery > selected_line.preparation_date_delivery:
                            if lines.preparation_time_delivery > selected_line.preparation_time_delivery:
                                    selected_line = lines
                        data = {
                                'id': lines.id,
                                'name': lines.name,
                                'product_id': [lines.product_id.id, lines.product_id.name] or False,
                                'product_uom_qty': lines.product_uom_qty,
                                'order_line_note': lines.order_line_note,
                                'order_line_state': lines.order_line_state,
                                'create_date': lines.create_date.astimezone(tz),
                                'order_partner_id': [lines.order_partner_id.id,
                                                     lines.order_partner_id.name] or False,
                                'pos_categ_id': lines.product_id.pos_categ_id.id,
                                'pos_categ_sequence': lines.product_id.pos_categ_id.sequence or 0,
                                'order_product_name': lines.order_product_name,
                                'price_unit': lines.price_unit,
                                'price_subtotal': lines.price_subtotal,
                                'preparation_time': lines.preparation_time,
                                'preparation_estimation': lines.preparation_date.astimezone(tz) + timedelta(hours=0, minutes=lines.preparation_time),
                                'is_optional': lines.product_id.is_optional_product or False,
                                'order_line_mark': lines.order_line_mark or False,
                                'checkout_note': lines.checkout_note or False,
                                # 'disable_print': lines.product_id.disable_print
                            }
                        list.append(data)
                        for option in lines.option_line_ids:
                            data = {
                                    'id': option.id,
                                    'name': option.name,
                                    'product_id': [option.product_id.id, option.product_id.name] or False,
                                    'product_uom_qty': option.product_uom_qty,
                                    'order_line_note': option.order_line_note,
                                    'order_line_state': option.order_line_state,
                                    'create_date': option.create_date.astimezone(tz),
                                    'order_partner_id': [option.order_partner_id.id,
                                                         option.order_partner_id.name] or False,
                                    'pos_categ_id': option.pos_categ_id,
                                    'pos_categ_sequence': option.product_id.pos_categ_id.sequence or 0,

                                    'order_product_name': option.order_product_name,
                                    'price_unit': option.price_unit,
                                    'price_subtotal': option.price_subtotal,
                                    'preparation_time': option.preparation_time,
                                    'preparation_estimation': option.preparation_date.astimezone(tz) + timedelta(
                                        hours=0, minutes=option.preparation_time),
                                    'is_optional': option.product_id.is_optional_product or False,
                                    'parent_line': lines.id or False,
                                    'icon': option.product_id.product_option_group.icon or False,
                                    # 'disable_print': lines.product_id.disable_print

                            }
                            optional_line.append(data)

                if len(list) > 0:
                    pick_up_time_delivery = datetime.strptime(str((i.date_order.astimezone(
                        tz) + timedelta(hours=0, minutes=selected_line.preparation_time)).replace(
                        tzinfo=None)), '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S')
                    order = {
                        'delivery_time': datetime.strptime(str((selected_line.preparation_date_delivery.astimezone(
                            tz) + timedelta(hours=0, minutes=selected_line.preparation_time_delivery)).replace(
                            tzinfo=None)),'%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S') if selected_line else False,
                        'order_id': [i.id, i.name] or False,
                        'delivery_boy': i.delivery_boy.name,
                        'pick_up_time_delivery': pick_up_time_delivery,
                        'customer': i.partner_id.name or False,
                        'website_delivery_type': i.website_delivery_type or False,
                        'checkout_note': i.checkout_note or False,
                        'pickup_date_string': i.pickup_date_string or False,
                        # 'updated_location': i.updated_location or False,
                        'state': i.state or False,
                        'vehicle_type': i.vehicle_type.type_name or False,
                        'vehicle_make': i.vehicle_make.make_name or False,
                        'approximate_location': i.approximate_location.location_name or False,
                        'location_notes': i.location_notes or False,
                        'vehicle_color': i.vehicle_color or False,
                        'license_plate_no': i.license_plate_no or False,
                        'order_time': t1.strftime('%H:%M'),
                        'preparation_time': i.preparation_time,
                        'type': 'sale',
                        'amount_untaxed': i.amount_untaxed,
                        'amount_tax': i.amount_tax,
                        'amount_total': i.amount_total,
                        'preparation_date': i.preparation_date,
                        'preparation_estimation': i.preparation_date.astimezone(tz) + timedelta(
                            hours=0, minutes=i.preparation_time),
                        'kitchen_screen': i.kitchen_screen,
                        'dine_in_table': i.dine_in_table.name,
                        'delivery_address_street': i.partner_shipping_id.street,
                        'delivery_address_street2': i.partner_shipping_id.street2,
                        'delivery_address_city': i.partner_shipping_id.city,
                        'delivery_address_state': i.partner_shipping_id.state_id.name,
                        'delivery_address_zip': i.partner_shipping_id.zip,
                        'delivery_address_country': i.partner_shipping_id.country_id.name,
                        'partner_contact': i.partner_id.phone,
                        'partner_email': i.partner_id.email,
                        'date_order': i.date_order,
                        'order_sequence': i.order_sequence,
                        'is_hubster': i.is_hubster or False,
                        'friendly_id': i.friendly_id or False,
                        'all_category': all_category,
                        'street': i.partner_id.street if i.partner_id else False,
                        'street2': i.partner_id.street2 if i.partner_id else False,
                        'city': i.partner_id.city if i.partner_id else False,
                        'zip': i.partner_id.zip if i.partner_id else False,
                        'cover': i.dine_in_table.seats if i.dine_in_table else False,
                        'floor': i.dine_in_table.floor_id.name if i.dine_in_table else False,


                    }

                    sorted_order_line = sorted(list, key=lambda k: k['pos_categ_sequence'])
                    # print_order_line_all = []
                    for pos_cat in config_id.printer_ids:
                        order_line = []
                        product_categories_ids = pos_cat.product_categories_ids.ids
                        for act_line in sorted_order_line:
                            act = act_line.copy()
                            if act['pos_categ_id'] in product_categories_ids:
                                # order_line.append(act_line)
                                optional_line_pos = []
                                for opt in optional_line:
                                    if act_line['id'] == opt['parent_line']:
                                        optional_line_pos.append(opt)
                                act['optional_line_pos'] = optional_line_pos
                                order_line.append(act)
                        if len(order_line) > 0:
                            order_pos = order.copy()
                            order_pos['order_line'] = order_line
                            ids = []
                            for i in order_line:
                                ids.append(i['id'])
                                for k in i['optional_line_pos']:
                                    ids.append(k['id'])
                            if bool(ids):
                                orders = request.env['sale.order.line'].sudo().browse(ids)
                                for o in orders:
                                    o.write({'order_line_state': 'done'})
                            order_pos['is_pass'] = pos_cat.is_pass_printer
                            order_pos['printer_name'] = pos_cat.name
                            so.append({pos_cat.id: order_pos})
        all_order = po+so
        return [all_order]


    @route('/order/print/update', type="json", auth="public", cors="*", csrf=False)
    def order_print_update(self, order):
        if bool(order):
            order=order[0]
            if order['type']=='pos':
                ids = []
                if 'order_line' in order:
                    for i in order['order_line']:
                        ids.append(i['id'])
                        for k in i['optional_line_pos']:
                            ids.append(k['id'])
                if bool(ids):
                    orders=request.env['pos.order.line'].sudo().browse(ids)
                    for o in orders:
                        o.write({'order_line_state':'done'})
            elif order['type']=='sale':
                ids = []
                if 'order_line' in order:
                    for i in order['order_line']:
                        ids.append(i['id'])
                        for k in i['optional_line_pos']:
                            ids.append(k['id'])
                if bool(ids):
                    orders = request.env['sale.order.line'].sudo().browse(ids)
                    for o in orders:
                        o.write({'order_line_state': 'done'})
        return True
