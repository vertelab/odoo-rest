odoo.define('rest_signport.signport', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SaleUpdateLineButton = publicWidget.Widget.extend({
        selector: '.o_portal_sale_sidebar',
        events: {
            'click button.start_signing_bankid2': '_onClick',
        },
        /**
         * Reacts to the click on the -/+ buttons
         *
         * @param {Event} ev
         */
        _onClick(ev) {
            ev.preventDefault();
            console.log("ERIDAN TEST");
        }
    });
    });