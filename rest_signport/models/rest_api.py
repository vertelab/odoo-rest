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
    customer_string = fields.Char(string="Customer signature label", default="Customer")
    employee_string = fields.Char(string="Employee signature label", default="Our company")


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


