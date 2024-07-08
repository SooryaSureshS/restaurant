import json

from odoo.http import Controller, route, request


class GetTableUser(Controller):

    @route('/table/user/get', type="json", auth="public", cors="*")
    def get_table_users(self, emp_id, table_id):
        user_obj = request.env['res.users'].sudo().browse(int(emp_id))
        if user_obj:
            user_obj.table_id = int(table_id)
        user_ids = request.env['res.users'].sudo().search([('table_id', '=', int(table_id))]).ids
        result = {}
        index = 1
        for i in user_ids:
            result[index] = {'id': i, 'status': False}
            index += 1
        result2 = {1: user_ids, 2: result}
        return result2
