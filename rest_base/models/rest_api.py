# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models
from urllib import request
from urllib.error import HTTPError, URLError
import json
import ssl

_logger = logging.getLogger(__name__)


class RestApi(models.Model):
    """Outgoing REST Integrations should create an instance of this
    model per API and call the function call_endpoint() to communicate
    with the API."""

    _name = "rest.api"
    _description = "Centralized model to make REST calls from Odoo."

    name = fields.Char(string="Name")
    url = fields.Char(string="URL", help="Base URL to the API")
    ssl_protocol = fields.Selection(
        string="SSL Protocol",
        selection=[
            ("no_verify", "None"),
            ("simple", "Simple"),
            ("mutual", "Mutual"),
        ],
    )
    ssl_certfile = fields.Char(string="Certfile", help="Path to the certfile")
    ssl_keyfile = fields.Char(string="Keyfile", help="Path to the keyfile")
    log_success = fields.Boolean(
        string="Log successes", help="If off, the code will only log errors"
    )
    log_count = fields.Integer(compute="_log_count", string="no. logs")

    def _log_count(self):
        for rec in self:
            rec.log_count = self.env["rest.log"].search_count(
                [("rest_api_id", "=", rec.id)]
            )

    def _generate_ctx(self):
        """Generates a context for our calls"""
        ctx = ssl.create_default_context()
        if self.ssl_protocol == "no_verify":
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        if self.ssl_protocol == "mutual":
            # TODO: untested code, test this
            # Define the client certificate settings for https connection
            # https://www.techcoil.com/blog/how-to-send-a-http-request-with-client-certificate-private-key-password-secret-in-python-3/
            ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ctx.load_cert_chain(certfile=self.ssl_certfile, keyfile=self.ssl_keyfile)
        elif self.ssl_protocol == "simple":
            # TODO: implement
            pass
        return ctx

    def call_endpoint(self, method, endpoint_url, headers={}, data_vals=None):
        """Handles calls to endpoints."""
        self.ensure_one()
        data_vals = json.dumps(data_vals).encode("utf-8") if data_vals else None
        ctx = self._generate_ctx()
        url = self.url + endpoint_url
        req = request.Request(url=url, data=data_vals, headers=headers, method=method)
        try:
            res_json = request.urlopen(req, context=ctx).read()
        except HTTPError as e:
            formatted_error = (
                f"HTTP error while sending message: {e.code} {e.reason}: {e.read()}"
            )
            log_id = self.create_log(
                endpoint_url=endpoint_url,
                headers=headers,
                method=method,
                data=data_vals,
                message=formatted_error,
                state="error",
            )
            _logger.exception(f"log created: {log_id.id}: " + formatted_error)
            return {"error": formatted_error}
        except URLError as e:
            formatted_error = f"URL error while sending message: {e.reason}"
            log_id = self.create_log(
                endpoint_url=endpoint_url,
                headers=headers,
                method=method,
                data=data_vals,
                message=formatted_error,
                state="error",
            )
            _logger.exception(f"log created: {log_id.id}: " + formatted_error)
            return {"error": formatted_error}
        except Exception as e:
            raise e

        if res_json:
            res = json.loads(res_json)
        else:
            res = False

        if self.log_success:
            log_id = self.create_log(
                endpoint_url=endpoint_url,
                headers=headers,
                method=method,
                data=data_vals,
                message=res,
                state="ok",
            )

        return res

    def create_log(self, endpoint_url, headers, method, data, message, state):
        self.ensure_one()
        log_vals = {
            "name": f"{method}: {self.url}{endpoint_url}",
            "rest_api_id": self.id,
            "state": state,
            "endpoint_url": endpoint_url,
            "headers": headers,
            "method": method,
            "data": data,
            "message": message,
        }
        return self.env["rest.log"].create(log_vals)

    def action_view_rest_log(self):
        action = self.env["ir.actions.actions"]._for_xml_id("rest_base.action_rest_log")
        action["domain"] = [("rest_api_id", "=", self.id)]
        return action

    def create_external_id(self, res_model, res_id, name):
        """Function to help create external ids"""
        self.ensure_one()
        if res_model and res_id and name:
            vals = {
                "module": "__import__",
                "model": res_model,
                "res_id": res_id,
                "name": name,
            }
            res = self.env["ir.model.data"].create(vals)
        else:
            res = False
        return res
