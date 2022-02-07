# -*- coding: utf-8 -*-

import logging
import base64
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import uuid

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

    def post_sign_sale_order(self, ssn, order_id, access_token, message=False, sign_type="customer", approval_id=False):
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
        # document_content = base64.b64decode(document.datas)
        _logger.warning(document_content)

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json; charset=utf8",
        }

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if sign_type == "customer":
            response_url = f"{base_url}/my/orders/{order_id}/sign_complete?access_token={access_token}"
        elif sign_type == "employee":
            response_url = f"{base_url}/web/{order_id}/{approval_id}/sign_complete?access_token={access_token}"
        _logger.warning("before add signature page")
        guid = str(uuid.uuid1())
        _logger.warning(f" {guid}")
        add_signature_page_vals = {
        "clientCorrelationId": guid,
        "documents": [
            {
            "content": document_content,
            "signaturePageTemplateId": "e33d2a21-1d23-4b4f-9baa-def11634ceb4",
            "signaturePagePosition": "last",
            }
        ]
        }

        # res = self.call_endpoint(
        #     method="POST",
        #     endpoint_url="/AddSignaturePage",
        #     headers=headers,
        #     data_vals=add_signature_page_vals,
        # )
        # _logger.warning(f"resresres: {res}")
        # document_content = res['documents'][0]['content']

        get_sign_request_vals = {
            "username": f"{self.user}",
            "password": f"{self.password}",
            "spEntityId": f"{self.sp_entity_id}",  # "https://serviceprovider.com/", # lägg som inställning på rest api
            "idpEntityId": f"{self.idp_entity_id}",  # "https://eid.test.legitimeringstjanst.se/sc/mobilt-bankid/",# lägg som inställning på rest api
            "signResponseUrl": response_url,
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
            # "signaturePage": {
            #     "initialPosition": "last",
            #     "templateId": "e33d2a21-1d23-4b4f-9baa-def11634ceb4",
            #     "allowRemovalOfExistingSignatures": False,
            #     "signerAttributes": {
            #         "name": "Byggare bob",
            #     },
            #     "signatureTitle": "Signed by",
            # },
        }
        res = self.call_endpoint(
            method="POST",
            endpoint_url="/GetSignRequest",
            headers=headers,
            data_vals=get_sign_request_vals,
        )
        return res

    def signport_post(self, data_vals={}, order_id=False, endpoint=False, sign_type="customer"):
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json; charset=utf8",
        }
        _logger.warning("signport post"*99)
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
        if not res['status']['success']:
            if 'not valid personal number' in res['status']['statusCodeDescription']:
                raise UserError('Invalid Personalnumber, please format it like "YYYYMMDDXXXX"')
            else:
                raise UserError(res)

        username = self.env.user.name
        document = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "sale.order"),
                    ("res_id", "=", order_id),
                    ("mimetype", "=", "application/pdf"),
                    ("name", "=", f"{self.env['sale.order'].browse(order_id).name}.pdf")
                ],
                limit=1,
            )
        )
        if sign_type == "employee":
            approval_line = self.env["approval.line"].search([("sale_order_id", "=", order_id), ("approver_id", "=", self.env.uid)], limit=1)
            approval_line.signed_document = res["document"][0]["content"]
            approval_line.signer_ca = res["signerCa"]
            approval_line.assertion = res["assertion"]
            approval_line.relay_state = base64.b64encode(res["relayState"].encode())
        else:
            _logger.warning("signport post else"*99)
            self.env["ir.attachment"].sudo().create(
                {
                    "name": f"{sign_type}: {self.env.user.name} - {document.display_name} - (Signed)",
                    "type": "binary",
                    "res_model": "sale.order",
                    "res_id": order_id,
                    "datas": res["document"][0]["content"],
                }
            )
            self.env["ir.attachment"].sudo().create(
                {
                    "name": f"{sign_type}: {self.env.user.name} - signerCa",
                    "type": "binary",
                    "res_model": "sale.order",
                    "res_id": order_id,
                    "datas": res["signerCa"],
                }
            )
            self.env["ir.attachment"].sudo().create(
                {
                    "name": f"{sign_type}: {self.env.user.name} - assertion",
                    "type": "binary",
                    "res_model": "sale.order",
                    "res_id": order_id,
                    "datas": res["assertion"],
                }
            )
            self.env["ir.attachment"].sudo().create(
                {
                    "name": f"{sign_type}: {self.env.user.name} - relayState",
                    "type": "binary",
                    "res_model": "sale.order",
                    "res_id": order_id,
                    "datas": base64.b64encode(res["relayState"].encode()),
                }
            )
            if sign_type == "customer":
                sale_order = self.env["sale.order"].sudo().browse(order_id)

                sale_order.signed_document = res["document"][0]["content"]
                sale_order.signer_ca = res["signerCa"]
                sale_order.assertion = res["assertion"]
                sale_order.relay_state = base64.b64encode(res["relayState"].encode())
                sale_order.write(
                    {
                        "signed_by": self.env.user.name,
                        "signed_on": datetime.now(),
                    }
                )
                sale_order.action_confirm()
                _logger.warning(sale_order.read())
        return res

class SaleOrder(models.Model):
    _inherit = "sale.order"

    signed_document = fields.Binary(string='Signed Document', readonly=1)
    signer_ca = fields.Binary(string='Signer Ca', readonly=1)
    assertion = fields.Binary(string='Assertion', readonly=1)
    relay_state = fields.Binary(string='Relay State', readonly=1)
