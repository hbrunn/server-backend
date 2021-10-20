odoo.define('base_push_notification', function (require) {
"use strict";

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');

    var BasePushNoticiationDemo = Widget.extend({
        tagName: 'li',
        attributes: {role: 'menuitem'},
        events: {
            'click a': '_onclick',
        },
        start: function() {
            if('serviceWorker' in navigator) {
                this.$el.append(jQuery('<a href="#">Request push</a>'));
            } else {
                this.$el.append(jQuery('Push notifications not supported'));
            }
        },
        _onclick: async function() {
            const registration = await navigator.serviceWorker.register(
                '/base_push_notification/static/src/js/worker.js'
            );
            const subscription = await registration.pushManager.subscribe();
            debugger;
            return this._rpc({
                route: '/base_push_notification/register',
                params: {
                    registration_type: 'generic',
                    identifier: subscription.endpoint,
                },
            });
        },
    });

    SystrayMenu.Items.push(BasePushNoticiationDemo);
})
