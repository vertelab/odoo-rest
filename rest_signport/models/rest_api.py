# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RestApiKnowit(models.Model):
    _inherit = "rest.api"

    def signport_get_sign_request(self):
        pass

    def signport_complete_signing(self):
        pass

    def test_connection(self):
        if self == self.env.ref("rest_signport.api_signport"):
            res = self.call_endpoint(method="GET", endpoint_url="/__Health", headers={"accept": "application/json"})
            _logger.warning("response"*99)
            _logger.warning(res)
            if res.get('code') == "200":
                raise UserError(_("Connection is working"))
            else:
                raise UserError(_("The connection is not working"))
        else:
            return super(RestApiAgresso, self).test_connection()

    def sign_with_bankid(self):
        res = self.call_endpoint(method="POST", endpoint_url="/GetSignRequest", headers={"accept": "application/json", "Content-Type": "application/json; charset=utf8"}, data_vals={
            "username": "Skogsstyrelsen",
            "password": "",
            "spEntityId": "https://serviceprovider.com/",
            "idpEntityId": "https://eid.test.legitimeringstjanst.se/sc/bankid-mock/",
            "signResponseUrl": "https://serviceprovider.com/handle-dss-response/",
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "loa": "http://id.swedenconnect.se/loa/1.0/uncertified-loa3",
            "certificateType": "PKC",
            "signingMessage": {
              "body": "Jag lovar och svär att jorden är nästan rund",
              "mustShow": True,
              "encrypt": True,
              "mimeType": "text"
            },
            "document": [
              {
                "mimeType": "application/xml",
                "content": "PHhtbD50ZXN0PC94bWw+",
                "adesType": "bes"
              }
            ],
            "requestedSignerAttribute": [
              {
                "name": "urn:oid:1.2.752.29.4.13",
                "type": "xsd:string",
                "value": "190102030400"
              }
            ]
        })
        html_form = base64.b64decode(res.get('eidSignRequest'))
        _logger.warning("response"*99)
        _logger.warning(res)
        _logger.warning(html_form)
        res2 = self.call_endpoint(method="POST", endpoint_url="/CompleteSigning", headers={"accept": "application/json", "Content-Type": "application/json; charset=utf8"}, data_vals={
            "username": "Skogsstyrelsen",
            "password": "",
            "relayState": res.get('relayState'),
            "eidSignResponse": res.get('eidSignRequest'),
            "binding": res.get('binding')
        })
        _logger.warning("response2"*99)
        _logger.warning(res)
