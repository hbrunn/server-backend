# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from pyfcm import FCMNotification

from odoo import fields, models


class PushNotificationConfig(models.Model):
    _name = "push.notification.config"
    _inherit = "mail.thread"
    _description = "Configuration for push notifications"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    debug = fields.Boolean()
    registration_ids = fields.One2many(
        "push.notification.registration",
        "push_config_id",
        string="Registrations",
    )
    registration_count = fields.Integer(
        compute=lambda self: [
            # TODO replace with read_group
            this.update(
                {
                    "registration_count": len(this.registration_ids),
                }
            )
            for this in self
        ],
    )
    use_fcm = fields.Boolean("Enable FCM")
    fcm_key = fields.Char("API key")
    fcm_topic = fields.Char("Topic")

    def _get_client(self, client_type):
        """ Return a client object for the request type of notification """
        self.ensure_one()
        if client_type == "fcm":
            # TODO
            return FCMNotification()
        else:
            raise NotImplementedError()
