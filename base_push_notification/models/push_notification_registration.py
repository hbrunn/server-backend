# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
import operator

from apns2.client import Notification as APNs2Notification
from apns2.payload import Payload as APNs2Payload, PayloadAlert as APNs2PayloadAlert

from odoo import _, api, exceptions, fields, models, tools


class PushNotificationRegistration(models.Model):
    _name = "push.notification.registration"
    _description = "Registered device"
    _rec_name = "identifier"
    _order = "push_config_id, identifier"

    registration_type = fields.Selection(
        [
            ("fcm", "FCM"),
            ("apns", "APNs"),
            ("generic", "Generic"),
        ],
        required=True,
    )
    push_config_id = fields.Many2one(
        "push.notification.config",
        required=True,
    )
    identifier = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")

    @api.constrains(
        "registration_type", "push_config_id.use_apns", "push_config_id.use_fcm",
        "push_config_id.use_generic",
    )
    def _check_registration_type(self):
        # TODO: this is probably too slow via the ORM
        for this in self:
            if not this.push_config_id["use_%s" % this.registration_type]:
                raise exceptions.ValidationError(
                    _(
                        "Configuration of registration %s does not support type %s",
                        this.identifier,
                        this.registration_type,
                    )
                )

    def push_notification(self, body, title=None, **kwargs):
        """ Send a notification to all devices in self """
        self.mapped("push_config_id").message_post(
            body=body,
            subtype_xmlid="base_push_notification.subtype_notification_content",
        )
        for reg_type, registrations in tools.groupby(
            self, operator.attrgetter("registration_type")
        ):
            registrations = self.browse(r.id for r in registrations)
            func = getattr(registrations, "_push_notification_%s" % reg_type)
            func(body, title=title or None, **kwargs)

    def grouped(self, groupby, chunks=100):
        """ Return self grouped by field groupby, and emit chunks records """
        for grouped, group in tools.groupby(self, operator.attrgetter(groupby)):
            for chunk in tools.split_every(chunks, group):
                yield grouped, self.browse(r.id for r in chunk)

    def _push_notification_apns(self, body, title=None, **kwargs):
        """ Send a notification to devices in self, which are of type apns """
        payload = APNs2Payload(
            alert=APNs2PayloadAlert(
                title=title,
                body=body,
            ),
            sound=kwargs.get("sound", "default"),
            badge=kwargs.get("badge", "1"),
        )
        for config, registrations in self.grouped("push_config_id"):
            client = config.sudo()._get_client("apns")
            result = client.send_notification_batch(
                registrations.mapped(
                    lambda x: APNs2Notification(payload=payload, token=x.identifier)
                ),
                topic=kwargs.get("topic", config.apns_topic or None),
            )
            # TODO: do something more sensible here
            config.message_post(
                body=json.dumps(result),
                subtype_xmlid="base_push_notification.subtype_notification_result",
            )

    def _push_notification_fcm(self, body, title=None, **kwargs):
        """ Send a notification to devices in self, which are of type fcm """
        for config, registrations in self.grouped("push_config_id"):
            client = config.sudo()._get_client("fcm")
            topic = kwargs.get("topic", config.fcm_topic or None)
            if topic:
                result = client.notify_topic_subscribers(
                    topic_name=topic,
                    message_body=body,
                    dry_run=config.debug,
                )
            else:
                result = client.notify_multiple_devices(
                    registration_ids=registrations.mapped("identifier"),
                    message_title=title,
                    message_body=body,
                )
            # TODO: do something more sensible here
            config.message_post(
                body=json.dumps(result),
                subtype_xmlid="base_push_notification.subtype_notification_result",
            )
            if topic:
                break

    def _push_notification_generic(self, body, title=None, **kwargs):
        """ Send a notification to devices in self, which are of type generic """
        for config, registrations in self.grouped("push_config_id"):
            client = config.sudo()._get_client("generic")
            # TODO: _get_client should return a function that adds the server key, vapid keys
