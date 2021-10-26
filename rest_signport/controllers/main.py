from odoo import http
from odoo.http import request
import json
import logging
_logger = logging.getLogger(__name__)

class KnowitController(http.Controller):

    @http.route(['/knowit/form'], type='json', auth="user", methods=['POST'])
    def knowit_form_view(self, **html_code):
        return request.env['product.template'].browse(int(product_template_id)).create_product_variant(product_template_attribute_value_ids)


    @http.route(['/my/orders/<int:order_id>/start_sign'], type='json', auth="public", website=True, methods=['POST'])
    def start_sign(self, order_id):
        _logger.warning("START SIGN!!!"*99)
        data = json.loads(request.httprequest.data)
        #data = {
        #    "ssn": "XXXXXXX-XXXX",
        #}
        #order_id
        res = {
            "html_code": "<div> boooo </div>"
        }
        res_json = json.dumps(res)
        return res_json
