# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os.path

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase


class TestFetchmailLocalMailbox(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.fetchmail_server = self.env["fetchmail.server"].create(
            {
                "name": "test server",
                "type": "local_mailbox",
                "mailbox_path": os.path.join(
                    get_module_path("fetchmail_local_mailbox"), "examples", "maildir",
                ),
                "mailbox_type": "maildir",
            }
        )
        self.env["ir.config_parameter"].set_param(
            "mail.catchall.domain", "fetchmail_local_mailbox_test",
        )
        self.env["mail.alias"].create(
            {
                "alias_name": "partner",
                "alias_model_id": self.env.ref("base.model_res_partner").id,
            }
        )

    def test_fetchmail(self):
        """Test mail  processing"""
        self.fetchmail_server.button_confirm_login()
        self.assertEqual(self.fetchmail_server.state, "done")
        partners = self.env["res.partner"].search([])
        self.fetchmail_server._fetch_mails()
        new_partners = self.env["res.partner"].search([]) - partners
        self.assertTrue(new_partners, "No new partner created")
