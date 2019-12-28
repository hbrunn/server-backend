# Copyright 2018 Therp BV <https://therp.nl>
# Copyright 2019-2020 initOS GmbH <https://initos.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from base64 import b64encode
from unittest import mock
from urllib.parse import urlparse

from odoo.addons.base_dav.controllers.main import Main as Controller
from odoo.tests.common import TransactionCase

from ..controllers.main import PREFIX

MODULE_PATH = "odoo.addons.base_dav"
CONTROLLER_PATH = MODULE_PATH + ".controllers.main"
RADICALE_PATH = MODULE_PATH + ".radicale"

ADMIN_PASSWORD = "RadicalePa$$word"


@mock.patch(CONTROLLER_PATH + ".request")
class TestBaseDav(TransactionCase):
    def setUp(self):
        super().setUp()

        self.collection = self.env["dav.collection"].create({
            "name": "Test Collection",
            "dav_type": "calendar",
            "model_id": self.env.ref("calendar.model_calendar_event").id,
            "domain": "[]",
        })

        self.controller = Controller()
        self.env.user.password_crypt = ADMIN_PASSWORD
        self.auth_string = b64encode(
            ("%s:%s" % (self.env.user.login, ADMIN_PASSWORD)).encode(),
        ).decode()

        patcher = mock.patch('odoo.http.request')
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_well_known(self, request_mock):
        request_mock.env = self.env

        response = self.controller.handle_well_known_request()
        self.assertEqual(response.status_code, 301)

    @mock.patch(RADICALE_PATH + ".auth.request")
    @mock.patch(RADICALE_PATH + ".collection.request")
    def test_base_dav(self, coll_mock, auth_mock, request_mock):
        request_mock.env = self.env
        request_mock.httprequest.environ = {
            "HTTP_AUTHORIZATION": "Basic %s" % self.auth_string,
            "REQUEST_METHOD": "PROPFIND",
            "HTTP_X_SCRIPT_NAME": PREFIX,
        }

        auth_mock.env["res.users"]._login.return_value = self.env.uid
        coll_mock.env = self.env

        dav_path = urlparse(self.collection.url).path.replace(PREFIX, '')

        response = self.controller.handle_dav_request(dav_path)
        self.assertGreaterEqual(response.status_code, 200)
        self.assertLess(response.status_code, 300)
