# -*- coding: utf-8 -*-

import logging
import base64
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RestApiSignport(models.Model):
    _inherit = "rest.api"

    def signport_get_sign_request(self):
        pass

    def signport_complete_signing(self):
        pass

    def test_connection(self):
        if self == self.env.ref("rest_signport.api_signport"):
            res = self.call_endpoint(
                method="GET",
                endpoint_url="/__Health",
                headers={"accept": "application/json"},
            )
            if res.get("status") == "up":
                raise UserError(_("Connection is working"))
            else:
                raise UserError(_("The connection is not working"))
        else:
            return super(RestApiSignport, self).test_connection()

    def post_sign_sale_order(self, ssn, order_id, message=False):
        document = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "sale.order"),
                ("res_id", "=", order_id),
                ("mimetype", "=", "application/pdf"),
            ],
            limit=1,
        )
        if not document:
            return False
        # TODO: attach pdf or xml of order to the request

        # document_content = "PHhtbD50ZXN0PC94bWw+"
        document_content = document.datas

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json; charset=utf8",
        }

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        data_vals = {
            "username": f"{self.user}",
            "password": f"{self.password}",
            "spEntityId": "https://serviceprovider.com/",
            "idpEntityId": "https://eid.test.legitimeringstjanst.se/sc/bankid-mock/",
            "signResponseUrl": f"{base_url}/signport/signing/complete",
            "signatureAlgorithm": "",
            "loa": "http://id.swedenconnect.se/loa/1.0/uncertified-loa3",
            "certificateType": "PKC",
            "signingMessage": {  # TODO: should we include the document here?
                "body": f"{message}",
                "mustShow": True,
                "encrypt": True,
                "mimeType": "text",
            },
            "document": [
                {
                    "mimeType": "application/xml",  # TODO: use pdf instead?
                    "content": document_content,  # TODO: include document to sign
                    # "fileName": False,  # TODO: add filename
                    # "encoding": False  # TODO: should we use this?
                    # "documentName": False # TODO: what is this used for?
                    "adesType": "bes",  # TODO: what is "ades"? "bes" or "none"
                }
            ],
            "requestedSignerAttribute": [
                {
                    "name": "urn:oid:1.2.752.29.4.13",  # swedish "personnummer", hardcoded
                    "type": "xsd:string",
                    "value": f"{ssn}",
                }
            ],
        }

        res = self.call_endpoint(
            method="POST",
            endpoint_url="/GetSignRequest",
            headers=headers,
            data_vals=data_vals,
        )
        html_form = base64.b64decode(res.get("eidSignRequest"))
        return res
