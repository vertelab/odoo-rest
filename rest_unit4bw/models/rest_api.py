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
            _logger.warning(res)
            if "1030" in res.get('response', {}):
                raise UserError(_("Connection is working"))
            else:
                raise UserError(_("The connection is not working"))
        else:
            return super(RestApiAgresso, self).test_connection()

    # def get_projects(self):
    #     res = self.call_endpoint(method="GET", endpoint_url="/v1/objects/projects")

    def agr_get_project(self, project):
        project_nr = "UV-2021-1"
        res = self.call_endpoint(method="GET", endpoint_url=f"/v1/projects/{project_nr}")

    def agr_put_project(self):
        # select = [
        #     {h
        #         "locationCode": "00656",
        #         "modelCode": "B345",
        #         "registrationNumber": "18LXSC",
        #     }
        # ]
        # data_vals = {
        #     "select": select,
        #     "filter": "registrationNumber eq '18LXSC'",
        #     "orderBy": "registrationNumber desc",
        #     "offset": 4,
        #     "limit": 5,
        # }
        data_vals = {}
        res = self.call_endpoint(
            method="PUT", endpoint_url="/v1/project", data_vals=data_vals
        )
