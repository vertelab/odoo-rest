# -*- coding: utf-8 -*-

import logging
import base64
import json
import uuid

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from datetime import datetime

_logger = logging.getLogger(__name__)


def _extend_header(headers, defaults):
    headers = headers or {}
    for k, v in defaults.items():
        if k not in headers:
            headers[k] = value
    return headers

class RestApiBest(models.Model):
    _name = "rest.api.best"
    _inherit = "rest.api"

    secret_token = fields.Char("Secret Token")

    def get_delivery_options(self, zip_code, country="SE", customer_identifier=None):
        endpoint = f"deliverydates/{country}/{zip_code}"
        return self.parse_resp("GET", endpoint, customer_identifier=customer_identifier)

    def get_all_delivery_options(self, country="SE", customer_identifier=None):
        endpoint = f"deliverydates/{country}"
        return self.parse_resp("GET", endpoint, customer_identifier=customer_identifier)

    def get_all_delivery_zones(self, customer_identifier=None):
        return self.parse_resp("GET", "", customer_identifier=customer_identifier)

    def parse_resp(self, method, endpoint_url, headers=None, data_vals=None, customer_identifier=None):
        try:
            resp = self.call_endpoint(method, endpoint, headers, data_vals, customer_identifier)
        except Exception as e: #TODO: Filter this except.
            _logger.exception(e)
            raise

        if resp.ok:
            try:
                return json.loads(resp.content)
            except json.decoder.JSONDecodeError as e:
                _logger.exception(e)
                raise UserError(_("Unexpected response from API.\n{resp_content}").format(resp_content=resp.content))
        else:
            raise UserError(_("Invalid response from API.\n{resp_content}").format(resp_content=resp.content))


    def call_endpoint(self, method, endpoint_url, headers=None, data_vals=None, customer_identifier=None):
        default_headers = {
                "X-API-Token": self.secret_token,
                "X-Customer-Identifier": customer_identifier or "UPPH1",
                }
        default_headers.update(headers) # Use this one!

        return super().call_endpoint(method, endpoint_url, default_headers, data_vals)

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


