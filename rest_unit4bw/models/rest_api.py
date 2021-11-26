# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class RestApiAgresso(models.Model):
    _inherit = "rest.api"

    def test_connection(self):
        if self == self.env.ref("rest_unit4bw.api_unit4bw"):
            res = self.call_endpoint(method="GET", endpoint_url="/v1/status")
            if "1030" in res.get("response", {}):
                raise UserError(_("Connection is working"))
            else:
                raise UserError(_("The connection is not working"))
        else:
            return super(RestApiAgresso, self).test_connection()

    def agr_post_project(self, data_vals):
        return self.call_endpoint(
            method="POST", endpoint_url="/v1/projects", data_vals=data_vals
        )
