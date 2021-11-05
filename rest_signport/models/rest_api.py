# -*- coding: utf-8 -*-

import logging
import base64
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

_logger = logging.getLogger(__name__)


class RestApiSignport(models.Model):
    _inherit = "rest.api"

    sp_entity_id = fields.Char(
        string="Service provider url", help="Link to our website (spEntityId)"
    )
    idp_entity_id = fields.Char(
        string="Lägitimerings tjänst url", help="Link to signing servide (idpEntityId)"
    )
    signature_algorithm = fields.Char(
        string="Signature algorithm",
        help="Link to signature algorithm (signatureAlgorithm)",
    )
    loa = fields.Char(string="Loa", help="Link to loa (loa)")
    api_type = fields.Selection(
        selection_add=[("signport", "Knowit signport")],
        ondelete={"signport": "set default"},
    )

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

    def post_sign_sale_order(self, ssn, order_id, access_token, message=False):
        # export_wizard = self.env['xml.export'].with_context({'active_model': 'sale.order', 'active_ids': order_id}).create({})
        # action = export_wizard.download_xml_export()
        # self.env['ir.attachment'].browse(action['res_id']).update({'res_id': order_id, 'res_model': 'sale.order'})

        document = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "sale.order"),
                    ("res_id", "=", order_id),
                    ("mimetype", "=", "application/pdf"),
                ],
                limit=1,
            )
        )
        if not document:
            return False
        # TODO: attach pdf or xml of order to the request

        # document_content = "PHhtbD50ZXN0PC94bWw+"
        document_content = document.datas.decode()
        _logger.warning(document_content)

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json; charset=utf8",
        }

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        data_vals = {
            "username": f"{self.user}",
            "password": f"{self.password}",
            "spEntityId": f"{self.sp_entity_id}",  # "https://serviceprovider.com/", # lägg som inställning på rest api
            "idpEntityId": f"{self.idp_entity_id}",  # "https://eid.test.legitimeringstjanst.se/sc/mobilt-bankid/",# lägg som inställning på rest api
            "signResponseUrl": f"{base_url}/my/orders/{order_id}/sign_complete?access_token={access_token}",
            "signatureAlgorithm": f"{self.signature_algorithm}",  # "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",# lägg som inställning på rest api
            "loa": f"{self.loa}",  # "http://id.swedenconnect.se/loa/1.0/uncertified-loa3",# lägg som inställning på rest api
            "certificateType": "PKC",
            "signingMessage": {
                "body": f"{message}",
                "mustShow": True,
                "encrypt": True,
                "mimeType": "text",
            },
            "document": [
                {
                    "mimeType": document.mimetype,  # TODO: check mime type
                    "content": document_content,  # TODO: include document to sign
                    "fileName": document.display_name,  # TODO: add filename
                    # "encoding": False  # TODO: should we use this?
                    "documentName": document.display_name,  # TODO: what is this used for?
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
        return res

    def signport_post(self, data_vals={}, order_id=False, endpoint=False):
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json; charset=utf8",
        }

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        data_vals["username"] = f"{self.user}"
        data_vals["password"] = f"{self.password}"
        res = self.call_endpoint(
            method="POST",
            endpoint_url=endpoint,
            headers=headers,
            data_vals=data_vals,
        )
        _logger.warning(f"FINAL res: {res}")
        document = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "sale.order"),
                    ("res_id", "=", order_id),
                    ("mimetype", "=", "application/pdf"),
                ],
                limit=1,
            )
        )
        self.env["ir.attachment"].sudo().create(
            {
                "name": f"{document.display_name} (Signed)",
                "type": "binary",
                "res_model": "sale.order",
                "res_id": order_id,
                "datas": res["document"][0]["content"],
            }
        )
        self.env["ir.attachment"].sudo().create(
            {
                "name": f"signerCa",
                "type": "binary",
                "res_model": "sale.order",
                "res_id": order_id,
                "datas": res["signerCa"],
            }
        )
        self.env["ir.attachment"].sudo().create(
            {
                "name": f"assertion",
                "type": "binary",
                "res_model": "sale.order",
                "res_id": order_id,
                "datas": res["assertion"],
            }
        )
        self.env["ir.attachment"].sudo().create(
            {
                "name": f"relayState",
                "type": "binary",
                "res_model": "sale.order",
                "res_id": order_id,
                "datas": base64.b64encode(res["relayState"].encode()),
            }
        )
        sale_order = self.env["sale.order"].sudo().browse(order_id)
        sale_order.update(
            {
                "state": "sale",
                "signed_by": self.env.user.name,
                "signed_on": datetime.now(),
            }
        )
        return res
