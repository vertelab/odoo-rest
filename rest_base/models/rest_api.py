# -*- coding: utf-8 -*-

import logging
import json
import ssl
import base64
from urllib import request
from urllib.error import HTTPError, URLError
from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class RestApi(models.Model):
    """Outgoing REST Integrations should create an instance of this
    model per API and call the function call_endpoint() to communicate
    with the API."""

    _name = "rest.api"
    _description = "Centralized model to make REST calls from Odoo."

    name = fields.Char(string="Name")
    user = fields.Char(string="User", help="A username for authentication, if needed.")
    password = fields.Char(
        string="Password", help="A password for authentication, if needed."
    )
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
    use_basic_auth = fields.Boolean(string="Use Basic Authentication")

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

    def call_endpoint(self, method, endpoint_url, headers=None, data_vals=None):
        """Handles calls to endpoints."""
        self.ensure_one()

        headers = headers or {}

        if self.use_basic_auth:
            # Use HTTP Basic access authentication
            b64_auth = base64.b64encode(bytes(f"{self.user}:{self.password}", "utf-8"))
            headers["Authorization"] = f"Basic {b64_auth.decode()}"

        data_vals = json.dumps(data_vals).encode("utf-8") if data_vals else None
        if data_vals:
            headers["Content-Type"] = "application/json"
        ctx = self._generate_ctx()
        url = self.url + endpoint_url
        req = request.Request(url=url, data=data_vals, headers=headers, method=method)
        try:
            res_json = request.urlopen(req, context=ctx).read()
        except HTTPError as e:
            e_read = e.read()
            formatted_error = (
                f"HTTP error while sending message: {e.code} {e.reason}: {e_read}"
            )
            log_vals = {
                "endpoint_url": endpoint_url,
                "headers": headers,
                "method": method,
                "data": data_vals,
                "message": formatted_error,
                "state": "error",
            }
            log_id = self.create_log(**log_vals)
            _logger.exception(f"log created: {log_id.id}: " + formatted_error)
            log_vals["response"] = f"{e.code} {e.reason}: {e_read}"
            return log_vals
        except URLError as e:
            formatted_error = f"URL error while sending message: {e.reason}"
            log_vals = {
                "endpoint_url": endpoint_url,
                "headers": headers,
                "method": method,
                "data": data_vals,
                "message": formatted_error,
                "state": "error",
            }
            log_id = self.create_log(**log_vals)
            _logger.exception(f"log created: {log_id.id}: " + formatted_error)
            log_vals["response"] = f"{e.reason}"
            return log_vals
        except ConnectionResetError as e:
            formatted_error = (
                f"URL error while sending message: {e.errno}: {e.strerror}"
            )
            log_vals = {
                "endpoint_url": endpoint_url,
                "headers": headers,
                "method": method,
                "data": data_vals,
                "message": formatted_error,
                "state": "error",
            }
            log_id = self.create_log(**log_vals)
            _logger.exception(f"log created: {log_id.id}: " + formatted_error)
            log_vals["response"] = f"{e.errno}: {e.strerror}"
            return log_vals
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

    def test_connection(self):
        """Tests the connection to the API.
        Should be implemented by each implementation of this module"""
        raise UserError(_("This API has no test defined."))

    def create_log(
        self, endpoint_url, headers, method, data, message, state, direction="out"
    ):
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        log_vals = {
            "name": f"{method}: {self.url}{endpoint_url}"
            if direction == "out"
            else f"{method}: {base_url}{endpoint_url}",
            "rest_api_id": self.id,
            "state": state,
            "endpoint_url": endpoint_url,
            "headers": headers,
            "method": method,
            "data": data,
            "message": message,
            "direction": direction,
        }
        return self.env["rest.log"].create(log_vals)

    def action_view_rest_log(self):
        action = self.env["ir.actions.actions"]._for_xml_id("rest_base.action_rest_log")
        action["domain"] = [("rest_api_id", "=", self.id)]
        return action

    def _create_external_id(self, module, res_model, res_id, name):
        """Function to help create external ids"""
        self.ensure_one()
        if res_model and res_id and name:
            vals = {
                "module": module,
                "model": res_model,
                "res_id": res_id,
                "name": name,
            }
            res = self.env["ir.model.data"].create(vals)
        else:
            res = False
        return res
