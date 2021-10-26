odoo.define('rest_signport.signport', function (require) {
    'use strict';


    var publicWidget = require('web.public.widget');

    publicWidget.registry.SaleUpdateLineButton = publicWidget.Widget.extend({
        selector: '.o_portal_sale_sidebar',
        events: {
            'click button#start_signing_bankid': '_onClick',
        },

        /**
         * Calls the route to get updated values of the line and order
         * when the quantity of a product has changed
         *
         * @private
         * @param {integer} order_id
         * @param {Object} params
         * @return {Deferred}
         */
        _callBankidSigninRoute(order_id, params) {
            return this._rpc({
                route: "/my/orders/" + order_id + "/start_sign",
                params: params,
            });
        },
        /**
         * @override
         */
        async start() {
            await this._super(...arguments);
            this.orderDetail = this.$el.find('table#sales_order_table').data();
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

            var ssn = $('#personnumber').val();
            console.log(ssn);

            this._callBankidSigninRoute(self.orderDetail.orderId, {
                'ssn': ssn,
                'sale_order': self.orderDetail.orderId,
            }).then((data) => {
              console.log(data);
              $('bankid_form').html(data['html']);
            });

        }
    });
    });
