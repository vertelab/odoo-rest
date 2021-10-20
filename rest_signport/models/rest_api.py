# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class RestApiAgresso(models.Model):
    _inherit = "rest.api"

    def signport_get_sign_request(self):
        pass

    def signport_complete_signing(self):
        pass