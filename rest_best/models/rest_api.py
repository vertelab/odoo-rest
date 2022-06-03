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
    _inherit = "rest.api"

    cn_or_api_key = fields.Char("CN or api key")
    customer_identifier = fields.Char("Customer Identifier")

    def get_delivery_options(self, zip_code, country="SE"):
        endpoint = f"deliverydates/{country}/{zip_code}"
        return self.parse_resp("GET", endpoint)

    def get_all_delivery_options(self, country="SE"):
        endpoint = f"deliverydates/{country}"
        return self.parse_resp("GET", endpoint)

    def get_all_delivery_zones(self):
        return self.parse_resp("GET", "")

    def parse_resp(self, method, endpoint_url, headers=None, data_vals=None):
        try:
            resp = self.call_endpoint(method, endpoint, headers, data_vals)
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


    def call_endpoint(self, method, endpoint_url, headers=None, data_vals=None):
        default_headers = {
                "X-API-Token": self.cn_or_api_key,
                "X-Customer-Identifier": self.customer_identifier or "UPPH1",
                }
        if headers:
            default_headers.update(headers)

        return super().call_endpoint(method, endpoint_url, default_headers, data_vals)

    def test_connection(self):
        # Currently the test does not end successfully, this code is here to indicate this for the installer
        raise UserError(self.call_endpoint("GET", ""))

