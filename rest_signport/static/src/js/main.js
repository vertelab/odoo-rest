odoo.define('rest_signport.signport', function (require) {
    'use strict';


    var publicWidget = require('web.public.widget');

    publicWidget.registry.SalePortalRestSignport = publicWidget.Widget.extend({
        selector: '.o_portal_sale_sidebar',
        events: {
            'click button#start_signing_bankid': '_onClick',
        },
        renderElement: function(){
            var self = this;
            this._super();
            // _.each(this.getChildren(), function(child){child.renderElement()});
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
                route: "/my/orders/" + order_id + "/sign_start",
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
            var self = this;

            var ssn = $('#personnumber').val();
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);

            this._callBankidSigninRoute(self.orderDetail.orderId, {
                'ssn': ssn.replace(/-/g, ''),
                'sale_order': self.orderDetail.orderId,
                'access_token': urlParams.get('access_token')
            }).then((data) => {
                if (data['status'] === 403) {
                    alert(data['message'])
                } else {
                    data = JSON.parse(data)
                    $('#relayState').val(data['relayState']);
                    $('#eidSignRequest').val(data['eidSignRequest']);
                    $('#binding').val(data['binding']);
                    $('#autosubmit').attr('action', data['signingServiceUrl']);
                    $('#autosubmit').submit();
                    // this.renderElement();
                }
            });
        }
    });
});
