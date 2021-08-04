# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Mobile push framework",
    "summary": "Send push notifications to registered clients",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Push notifications",
    "website": "https://github.com/OCA/server-backend",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": ["apns2", "pyfcm"],
    },
    "depends": [
        "mail",
        "queue_job",
    ],
    "data": [
        "security/base_push_notification_security.xml",
        "security/ir.model.access.csv",
        "wizards/push_notification_send.xml",
        "views/push_notification_registration.xml",
        "views/push_notification_config.xml",
        "views/menu.xml",
        "data/mail_message_subtype.xml",
    ],
}
