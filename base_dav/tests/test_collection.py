# Copyright 2019-2020 initOS GmbH <https://initos.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta
from unittest import mock

from odoo.addons.base_dav.radicale.collection import Collection
from odoo.exceptions import MissingError
from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestCalendar(TransactionCase):
    def setUp(self):
        super().setUp()

        self.collection = self.env["dav.collection"].create({
            "name": "Test Collection",
            "dav_type": "calendar",
            "model_id": self.env.ref("calendar.model_calendar_event").id,
            "domain": "[]",
        })

        self.create_field_mapping(
            "summary", "calendar.field_calendar_event_name",
            excode="result = record.name",
            imcode="result = item.value",
        )
        self.create_field_mapping(
            "dtstart", "calendar.field_calendar_event_start",
        )
        self.create_field_mapping(
            "dtend", "calendar.field_calendar_event_stop",
        )

        start = datetime.now()
        stop = start + timedelta(hours=1)
        self.event = self.env["calendar.event"].create({
            "name": "Test Event",
            "start": start.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            "stop": stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        })

    def create_field_mapping(self, name, field_ref, imcode=None, excode=None):
        return self.env["dav.collection.field_mapping"].create({
            "collection_id": self.collection.id,
            "name": name,
            "field_id": self.env.ref(field_ref).id,
            "mapping_type": "code" if imcode or excode else "simple",
            "import_code": imcode,
            "export_code": excode,
        })

    def compare_event(self, vobj, event=None):
        record = self.collection.from_vobject(vobj)

        self.assertEqual((event or self.event).name, record["name"])
        self.assertEqual((event or self.event).start, record["start"])
        self.assertEqual((event or self.event).stop, record["stop"])

    def test_import_export(self):
        # Exporting and importing should result in the same event
        vobj = self.collection.to_vobject(self.event)
        self.compare_event(vobj)

    def test_get_record(self):
        rec = self.collection.get_record([self.event.id])
        self.assertEqual(rec, self.event)

        self.collection.field_uuid = self.env.ref(
            "calendar.field_calendar_event_name",
        ).id
        rec = self.collection.get_record([self.event.name])
        self.assertEqual(rec, self.event)

    @mock.patch("odoo.addons.base_dav.radicale.collection.request")
    def test_collection(self, request_mock):
        request_mock.env = self.env
        collection_url = "/%s/%s" % (self.env.user.login, self.collection.id)
        collection = list(Collection.discover(collection_url))[0]

        # Try to get the test event
        event_url = "%s/%s" % (collection_url, self.event.id)
        self.assertIn(event_url, collection.list())

        # Get the test event using the URL and compare it
        item = collection.get(event_url)
        self.compare_event(item.item)
        self.assertEqual(item.href, event_url)

        # Get a non-existing event
        self.assertFalse(collection.get(event_url + "0"))

        # Get the event and alter it later
        item = self.collection.to_vobject(self.event)
        self.event.name = "Different Name"
        with self.assertRaises(AssertionError):
            self.compare_event(item)

        # Restore the event
        item = collection.upload(event_url, item)
        self.compare_event(item.item)

        # Create a new event
        item = collection.upload(event_url + "0", item)
        event = self.collection.get_record(collection._split_path(item.href))
        self.assertNotEqual(event, self.event)
        self.compare_event(item.item, event)

        # Delete an event
        collection.delete(item.href)
        with self.assertRaises(MissingError):
            event.name
