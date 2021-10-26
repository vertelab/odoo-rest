odoo.define('rest_signport.RestSignBankid', function (require) {
'use strict';

var concurrency = require('web.concurrency');
var core = require('web.core');
var utils = require('web.utils');
var ajax = require('web.ajax');
var _t = core._t;


var publicWidget = require("web.public.widget");
 var Widget = require('web.Widget');
 var core = require('web.core');
 var session = require('web.session');
// var RestSignBankid;

// return window.addEventListener('load', function () {
//   console.log("It's loaded!")
//   console.log(document.getElementById('start_signing_bankid'))
//
// })
console.log(document.getElementById('start_signing_bankid2'));
publicWidget.registry.RestSignBankid = publicWidget.Widget.extend({
    template: 'RestSignBankid',
    init: function(parent, options){
            this._super.apply(this, arguments);
            var self = this;
            console.log("init")
        },
    events: {
        'click . start_signing_bankid2': '_startSigningBankid',
    },
    renderElement: function(){
            var self = this;
            this._super();
            this.$('button#start_signing_bankid2').click(() => {
                console.log("WOOO WEEE")
            })
        },
    // renderElement: function(){
    //     console.log("rendering")
    //       var self = this;
    //       this._super();
    //       this.$('#start_signing_bankid').click(function(){self._startSigningBankid()});
    //       //
    //       // _.each(this.getChildren(), function(child){child.renderElement()});
    //   },

    _startSigningBankid: function (ev) {
        var self = this;
        console.log("data:");
        console.log(this.data);
        console.log("ssn:");
        console.log($('#personnumber'));


        // var sale_order = this.data.id
        // var ssn = $('#personnumber');

        // var data = ajax.jsonRpc(this._getUri('/my/orders/'+sale_order+'/start_sign'), 'call', {
        //     'ssn': ssn,
        //     'sale_order': sale_order,
        // })
        // console.log(data)
        // return True
    }
});
// publicWidget.registry.RestSignBankid._startSigningBankid("hej");
return publicWidget.registry.RestSignBankid;
});
