# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
import operator

from odoo import _, api, exceptions, fields, models, tools


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    push_notification_registration_ids = fields.One2many(
        'push.notification.registration', 'partner_id',
        string='Push notification registrations',
    )

    def action_push_notification_registrations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Push registrations'),
            'res_model': 'push.notification.registration',
            'domain': [('partner_id', 'in', self.ids)],
            'context': {
                'default_partner_id': self[:1].id,
            },
            'views': [(False, 'list')],
        }
