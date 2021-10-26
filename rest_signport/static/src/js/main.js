odoo.define('rest_signport.signport', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.SaleUpdateLineButton = publicWidget.Widget.extend({
        selector: '.o_portal_sale_sidebar',
        events: {
            'click button#start_signing_bankid': '_onClick',
        },
        /**
         * Reacts to the click on the -/+ buttons
         *
         * @param {Event} ev
         */
        _onClick(ev) {
            ev.preventDefault();
            console.log("ERIDAN TEST");
            var self = this;
            console.log("data:");
            console.log(this.data);
            console.log("ssn:");
            console.log($('#personnumber'));
            var sale_order = this.data.id;
            var ssn = $('#personnumber');

            var data = ajax.jsonRpc(this._getUri('/my/orders/'+sale_order+'/start_sign'), 'call', {
                'ssn': ssn,
                'sale_order': sale_order,
            })
            console.log(data);
            document.getElementById('bankid_form').html(data['html']);
        }
    });
    });
