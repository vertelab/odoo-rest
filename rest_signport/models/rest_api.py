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
        string="Identity service url", help="Link to identity service (idpEntityId)"
    )
    signature_algorithm = fields.Char(
        string="Signature algorithm",
        help="Link to signature algorithm (signatureAlgorithm)",
    )
    loa = fields.Char(string="Levels of assurance", help="Link to levels of assurance (loa)")
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


