# -*- coding: utf-8 -*-

import logging
from odoo import _, api, fields, models
from urllib import request
from urllib.error import HTTPError, URLError
import json
import ssl

_logger = logging.getLogger(__name__)

# dict used to store fields we are syncing for offices and their mapping
OFFICE_MAP = {
    "name": "arbetsplatsNamn",
    "street": "besoksadress",
    "zip": "postnr",
    "city": "postort",
}
# TODO: this dict needs work.
DEPARTMENT_MAP = {
    "name": "orgEnhetNamn",
    "manager_id": "stfChef"
}


class RestApiKdb(models.Model):
    _inherit = "rest.api"

    def sync_kontorsdatabas_data(self):
        # TODO: delete these comments
        # Tänkt struktur
        # GET /api/kontor -> Mappa mot res.partner
        # GET /api/enhet -> Mappa mot hr.department
        # GET /api/person/enhet/{orgenhetNr} -> mappa mot res.user och länka sedan till deras "res_partner.parent_id"
        # GET /api/person/enhet/{orgenhetNr} -> mappa mot hr.employee och mappa mot deras hr.department

        department_nr = False

        res_offices = self.call_endpoint(method="GET", endpoint_url="/api/kontor")
        # [
        #     {
        #         "arbetsplatsnr": 0,
        #         "arbetsplatsNamn": "string",
        #         "besoksadress": "string",
        #         "postadress": "string",
        #         "postnr": "string",
        #         "postort": "string",
        #         "tillfalligt": true,  #  TODO: should we read this?
        #     }
        # ]
        for office in res_offices:
            # check if res.partner exists
            office_id = False
            office_ext_id = "office_" + office.get("arbetsplatsnr")
            # self.env.ref might be slow? maybe use
            # self.external_id_to_res_id() instead
            office_id = self.env.ref("__import__." + office_ext_id)
            if office_id:
                # Office exists, check if values are in sync
                # TODO: This comparison code is repeated.
                # Maybe create a function for it.
                office_dict = office_id.read()[0]
                write_vals = {}
                for office_key in OFFICE_MAP:
                    # compare stored value to value from our request
                    # for each key in the OFFICE_MAP
                    res_value = office.get(OFFICE_MAP[office_key])
                    odoo_value = office_dict[office_key]
                    if res_value and odoo_value != res_value:
                        # there's a diff we need to fix
                        write_vals[office_key] = res_value
                # do the write if we have data to update.
                if write_vals:
                    office_id.write(write_vals)
            else:
                # office missing, create new
                office_vals = {
                    "name": office.get(OFFICE_MAP["name"]),
                    "street": office.get(OFFICE_MAP["street"]),
                    "zip": office.get(OFFICE_MAP["zip"]),
                    "city": office.get(OFFICE_MAP["city"]),
                    "country_id": self.env.ref("base.se").id,  # hardcoded to Sweden.
                }
                office_id = self.env["res.partner"].create(office_vals)
                self.create_external_id(office_id._name, office_id.id, office_ext_id)

        res_departments = self.call_endpoint(method="GET", endpoint_url="/api/enhet")
        # [
        #     {
        #         "orgEnhetNr": "string",
        #         "orgEnhetNamn": "string",
        #         "orgStruktur": "string",
        #         "enhetschef": "string",
        #         "stfChef": "string",
        #         "stfChef2": "string",
        #     }
        # ]
        for department in res_departments:
            # check if hr.department exists
            department_id = False
            department_ext_id = "department_" + department.get("orgEnhetNr")
            # self.env.ref might be slow? maybe use
            # self.external_id_to_res_id() instead
            department_id = self.env.ref("__import__." + department_ext_id)
            if department_id:
                # Office exists, check if values are in sync
                department_dict = department_id.read()[0]
                write_vals = {}
                for department_key in DEPARTMENT_MAP:
                    # compare stored value to value from our request
                    # for each key in the DEPARTMENT_MAP
                    res_value = department.get(DEPARTMENT_MAP[department_key])
                    odoo_value = department_dict[department_key]
                    if res_value and odoo_value != res_value:
                        # there's a diff we need to fix
                        write_vals[department_key] = res_value
                # do the write if we have data to update.
                if write_vals:
                    department_id.write(write_vals)
            else:
                # department missing, create new
                depart_vals = {
                    "name": office.get(DEPARTMENT_MAP["name"]),
                    "manager_id": office.get(
                        DEPARTMENT_MAP["manager_id"]
                    ),  # TODO: fix this, this wont work
                }
                department_id = self.env["hr.department"].create(depart_vals)
                self.create_external_id(
                    department_id._name, department_id.id, department_ext_id
                )

        res_persons = self.call_endpoint(
            method="GET", endpoint_url=f"/api/person/enhet/{department_nr}"
        )
        # [
        #     {
        #         "login": "string",
        #         "namn": "string",
        #         "fornamn": "string",
        #         "efternamn": "string",
        #         "befattning": "string",
        #         "arbetsuppgifter": ["string"],
        #         "orgEnhetNr": "string",
        #         "orgEnhetNamn": "string",
        #         "epost": "string",
        #         "chef": "string",
        #         "kontor": {
        #             "arbetsplatsnr": 0,
        #             "arbetsplatsNamn": "string",
        #             "besoksadress": "string",
        #             "postadress": "string",
        #             "postnr": "string",
        #             "postort": "string",
        #             "tillfalligt": true,
        #         },
        #         "isChef": true,
        #         "isStf": true,
        #         "isStf2": true,
        #         "efhid": "string",
        #         "anstTomDatum": "2021-10-01T14:57:51.589Z",
        #     }
        # ]
        for preson in res_persons:
            # check if res.partner exists
            # check if values are the same
            # create new, update data, or do nothing

            # check if hr.employee exists
            # check if values are the same
            # create new, update data, or do nothing
            pass
