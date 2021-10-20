# copied code from https://github.com/OCA/rest-framework

import datetime
import decimal
import json
from odoo.http import HttpRequest


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202,arguments-differ
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(JSONEncoder, self).default(obj)


class HttpRestRequest(HttpRequest):
    def make_json_response(self, data, headers=None, cookies=None):
        data = JSONEncoder().encode(data)
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/json"
        return self.make_response(data, headers=headers, cookies=cookies)
