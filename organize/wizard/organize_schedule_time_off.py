# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class OrganizeScheduleTimeOff(models.TransientModel):
    _name = 'organize.schedule.time.off'
    _description = "Organize Schedule Time Off"

    def action_discard(self):
        self.env['organize.slot'].search([('id', '=', self.env.context.get('organize_slot_id'))]).unlink()
        return {
            'name': ' ',
            'type': 'ir.actions.act_window',
            'res_model': 'organize.slot',
            'views': [(self.env.ref('organize.organize_view_form_in_gantt').id, 'form')],
            'target': 'new',
        }

    def action_yes(self):
        organize_slot = self.env['organize.slot'].search([('id', '=', self.env.context.get('organize_slot_id'))])
        function = self.env.context.get('function')
        if function == "action_send":
            organize_slot.with_context(
                function="action_yes",
                condition_check=False
            ).action_send()
        if function == "action_publish":
            organize_slot.with_context(
                function="action_yes",
                condition_check=False
            ).action_publish()
        return {
            'name': ' ',
            'type': 'ir.actions.act_window',
            'res_model': 'organize.slot',
            'nodestroy': True,
            'views': [(self.env.ref('organize.organize_view_gantt').id, 'form')],
            'target': 'current',
        }
