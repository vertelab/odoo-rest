# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class RestLog(models.Model):
    _name = "rest.log"
    _description = "Logs events for rest.api calls"
    _order = "create_date DESC"

    name = fields.Char(string="Name")
    rest_api_id = fields.Many2one(comodel_name="rest.api", string="API")
    endpoint_url = fields.Char(string="Endpoint")
    method = fields.Char(string="Method")
    headers = fields.Text(string="Headers")
    data = fields.Text(string="Data")
    message = fields.Text(string="Message")
    state = fields.Selection(
        string="State", selection=[("error", "Error"), ("ok", "OK")]
    )
    direction = fields.Selection(
        string="Direction", selection=[("in", "In"), ("out", "Out")], default="out"
    )
