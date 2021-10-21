# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RestApiAgresso(models.Model):
    _inherit = "rest.api"

    def signport_get_sign_request(self):
        pass

    def signport_complete_signing(self):
        pass

    def test_connection(self):
        if self == self.env.ref("rest_signport.api_signport"):
            res = self.call_endpoint(method="get", endpoint_url="/__Health", headers={"accept": "application/json"})
            _logger.warning("response"*99)
            _logger.warning(res)
            if res.get('code') == "200":
                raise UserError(_("Connection is working"))
            else:
                raise UserError(_("The connection is not working"))
        else:
            return super(RestApiAgresso, self).test_connection()
