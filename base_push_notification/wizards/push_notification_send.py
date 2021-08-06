# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PushNotificationSend(models.TransientModel):
    _name = "push.notification.send"
    _description = "Send push notifications"

    title = fields.Char()
    text = fields.Text(required=True)
    asynchronous = fields.Boolean(default=False)

    def action_send(self):
        self.ensure_one()
        active_model = self.env.context.get("active_model")
        registrations = self.env["push.notification.registration"]
        if active_model == "push.notification.registration":
            if self.env.context.get("active_domain"):
                registrations = registrations.search(self.env.context["active_domain"])
            else:
                registrations = registrations.browse(
                    self.env.context.get("active_ids", [])
                )
        elif active_model == "push.notification.configuration":
            # TODO: implement
            raise NotImplementedError()
        else:
            raise NotImplementedError()
        if self.asynchronous:
            registrations = registrations.with_delay()
        return registrations.push_notification(self.text, title=self.title)
