from odoo import fields, http, _
from odoo.http import request
import json

import base64
from odoo.exceptions import AccessError, MissingError
import binascii
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv import expression
from odoo.exceptions import UserError
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
    get_records_pager,
)

import logging
_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):
    @http.route(['/my/orders/<int:order_id>'], type='http', auth="user", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type,
                                     report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Quotation viewed by customer %s', order_sudo.partner_id.name)
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = self._order_get_page_view_values(order_sudo, access_token, **kw)
        values['message'] = message

        return request.render('sale.sale_order_portal_template', values)


class KnowitController(http.Controller):
    def _order_get_page_view_values(self, order, access_token, **kwargs):
        _logger.warning("1"*50) #HERE
        values = {
            "sale_order": order,
            "token": access_token,
            "return_url": "/shop/payment/validate",
            "bootstrap_formatting": True,
            "partner_id": order.partner_id.id,
            "report_type": "html",
            "action": order._get_portal_return_action(),
        }
        if order.company_id:
            values["res_company"] = order.company_id

        if order.has_to_be_paid():
            domain = expression.AND(
                [
                    [
                        "&",
                        ("state", "in", ["enabled", "test"]),
                        ("company_id", "=", order.company_id.id),
                    ],
                    [
                        "|",
                        ("country_ids", "=", False),
                        ("country_ids", "in", [order.partner_id.country_id.id]),
                    ],
                ]
            )
            acquirers = request.env["payment.acquirer"].sudo().search(domain)

            values["acquirers"] = acquirers.filtered(
                lambda acq: (acq.payment_flow == "form" and acq.view_template_id)
                or (acq.payment_flow == "s2s" and acq.registration_view_template_id)
            )
            values["pms"] = request.env["payment.token"].search(
                [("partner_id", "=", order.partner_id.id)]
            )
            values["acq_extra_fees"] = acquirers.get_acquirer_extra_fees(
                order.amount_total, order.currency_id, order.partner_id.country_id.id
            )

        if order.state in ("draft", "sent", "cancel"):
            history = request.session.get("my_quotations_history", [])
        else:
            history = request.session.get("my_orders_history", [])
        values.update(get_records_pager(history, order))

        return values

    def get_signport_api(self):
        return request.env.ref("rest_signport.api_signport")

    @http.route(
        ["/my/orders/<int:order_id>/sign_complete"],
        type="http",
        auth="user",
        methods=["POST"],
        csrf=False,
        website=True,
    )
    def complete_signing(self, order_id, access_token, **res):
        _logger.warning("2"*50) #HERE
        html_form = base64.b64decode(res.get("EidSignResponse")).decode()
        data = {
            "relayState": res["RelayState"],
            "eidSignResponse": res["EidSignResponse"],
            "binding": res["Binding"],
        }
        _logger.warning("complete_signing controller"*10)
        api_signport = self.get_signport_api()
        res = api_signport.sudo().signport_post(data, order_id, "/CompleteSigning") 
        res_json = json.dumps(res)
        try:
            order_sudo = request.env["sale.order"].sudo().browse(order_id)
        except (AccessError, MissingError):
            return request.redirect("/my")

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get("view_quote_%s" % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session["view_quote_%s" % order_sudo.id] = now
                body = _("Quotation viewed by customer %s", order_sudo.partner_id.name)
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = self._order_get_page_view_values(order_sudo, access_token, **res)
        # values['message'] = message

        return request.render("sale.sale_order_portal_template", values)

    @http.route(
        ["/my/orders/<int:order_id>/sign_start"],
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def start_sign(self, order_id):
        uid = http.request.env.context.get('uid')
        logging.info(f"start_sign === {type(uid)} === {uid}")

        if uid == 4:
            res_json = {
                'message': 'There is a problem try to sign this document. Reload Page to Confirm you are logged In',
                'status': 403
            }
        else:
            data = json.loads(request.httprequest.data)
            ssn = data.get("params", {}).get("ssn")
            if not ssn:
                return False
            api_signport = self.get_signport_api()
            res = api_signport.sudo().post_sign_sale_order(
                ssn=ssn,
                order_id=order_id,
                access_token=data.get("params", {}).get("access_token"),
                message="Signering av dokument",
            )
            res_json = json.dumps(res)
        return res_json
