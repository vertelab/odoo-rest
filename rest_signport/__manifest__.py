# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Rest: SignPort',
    'version': '14.0.1.0.1',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Implements REST calls to the SignPort API.',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'REST',
    'description': """
Implements REST calls to the SignPort API.
14.0.0.0.1 - Added a few sudo() calls and pep8-formatted
14.0.0.0.0 - Initial version
    """,
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-rest/rest_signport',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-rest',
    # Any module necessary for this one to work correctly
    "depends": [
        "rest_base",
        "sale",
        "portal",
        "base_automation",
    ],
    "data": [
        "data/rest_api_data.xml",
        'views/sale_order_portal_templates.xml',
    ],
    # 'qweb': [
    #     'static/src/xml/base.xml'
    # ],
    "demo": [],
    "installable": True,
    "application": False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
