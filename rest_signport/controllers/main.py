from odoo import http
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)

class KnowitController(http.Controller):

    def get_signport_api(self):
        return request.env.ref("rest_signport.api_signport")

    @http.route(['/signport/signing/complete'], type='json', auth="public", methods=['POST'])
    def complete_signing(self, **html_code):
        _logger.error(html_code)
        data = json.loads(request.httprequest.data)
        _logger.error(data)


    @http.route(['/my/orders/<int:order_id>/start_sign'], type='json', auth="public", website=True, methods=['POST'])
    def start_sign(self, order_id):
        _logger.warning(order_id)
        data = json.loads(request.httprequest.data)
        _logger.warning(data)
        ssn = data.get("params", {}).get("ssn")
        if not ssn:
            return False
        api_signport = self.get_signport_api()
        res = api_signport.post_sign_sale_order(ssn=ssn, order_id=order_id, message="Test message.")
        _logger.warning(res)
        res_json = json.dumps(res)
        return res_json
