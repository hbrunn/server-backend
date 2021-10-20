# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import Controller, request, route


class PushNotificationController(Controller):
    @route('/base_push_notification/register', type='json', auth='public')
    def register(self, **kwargs):
        """
        Register a device for notifications
        """
        # TODO use some other authentication scheme when user is public
        # TODO more checks
        request.env['push.notification.registration'].create(kwargs)
