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

    def post_sign_request(self, ssn):
        headers = {
                "accept": "application/json",
                "Content-Type": "application/json; charset=utf8",
            }

        base_url = "https://serviceprovider.com"

        data_vals = {
            "username": f"{self.user}",
            "password": f"{self.password}",
            "spEntityId": "https://serviceprovider.com/",
            "idpEntityId": "https://eid.test.legitimeringstjanst.se/sc/bankid-mock/",
            "signResponseUrl": f"{base_url}/signport/signing/complete",
            "signatureAlgorithm": "",
            "loa": "http://id.swedenconnect.se/loa/1.0/uncertified-loa3",
            "certificateType": "PKC",
            "signingMessage": {
                "body": "Jag lovar och svär att jorden är nästan rund",
                "mustShow": True,
                "encrypt": True,
                "mimeType": "text",
            },
            "document": [
                {
                    "mimeType": "application/xml",
                    "content": "PHhtbD50ZXN0PC94bWw+",
                    "adesType": "bes",
                }
            ],
            "requestedSignerAttribute": [
                {
                    "name": "urn:oid:1.2.752.29.4.13",
                    "type": "xsd:string",
                    "value": "190102030400",
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
