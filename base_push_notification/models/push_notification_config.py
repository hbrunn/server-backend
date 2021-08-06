# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from apns2.client import APNsClient
from apns2.credentials import TokenCredentials as APNsTokenCredentials
from pyfcm import FCMNotification

from odoo import fields, models


class PushNotificationConfig(models.Model):
    _name = "push.notification.config"
    _inherit = "mail.thread"
    _description = "Configuration for push notifications"
    _order = "name"

    name = fields.Char(required=True)
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
    use_apns = fields.Boolean("Enable APNs")
    apns_key = fields.Text("Key")
    apns_key_id = fields.Char("Key ID")
    apns_team_id = fields.Char("Team ID")
    apns_topic = fields.Char("Topic")

    def _get_client(self, client_type):
        """ Return a client object for the request type of notification """
        self.ensure_one()
        if client_type == "apns":
            credentials = APNsTokenCredentials(
                auth_key_path=None,
                auth_key_id=self.apns_key_id,
                team_id=self.apns_team_id,
            )
            # the lib doesn't support in memory keys
            credentials._TokenCredentials__auth_key = self.apns_key
            return APNsClient(
                credentials=credentials,
                use_sandbox=self.debug,
            )
        elif client_type == "fcm":
            return FCMNotification(api_key=self.fcm_key)
        else:
            raise NotImplementedError()
