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
            if "1030" in res.get("response", {}):
                raise UserError(_("Connection is working"))
            else:
                raise UserError(_("The connection is not working"))
        else:
            return super(RestApiAgresso, self).test_connection()

    def agr_get_project(self, project):
        project_nr = "UV-2021-1"
        res = self.call_endpoint(
            method="GET", endpoint_url=f"/v1/projects/{project_nr}"
        )

    def agr_post_project(self, project_nr):
        data_vals = {
            "projectName": "TestProject",
            "costCentre": "TestCosts",
            "projectManagerId": "1",
            "projectId": f"UV-2021-{project_nr}",
            "hasActivities": False,
            "postTimeCosts": False,
            "hasTimeSheetLimitControl": False,
            "isGlobalProject": False,
            "authoriseNormalHours": False,
            "authoriseOvertime": False,
            "probability": 0.0,
            "isSupportingProject": False,
            "hasTemplate": False,
            "containsWorkOrders": False,
            "activities": [],
            "globalProjectInformation": [],
            "relatedValues": [],
        }
        res = self.call_endpoint(
            method="POST", endpoint_url="/v1/projects", data_vals=data_vals
        )
