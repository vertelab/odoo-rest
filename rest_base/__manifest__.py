# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Enterprise Management Solution, third party addon
#    Copyright (C) 2014-2021 Vertel AB (<http://vertel.se>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Rest base",
    "description": """
Implements a standardized way to call REST APIs from Odoo and logs errors.
14.0.1.3.0 - Added better error handling
14.0.1.2.0 - Added a button for testing the connection to the API
14.0.1.1.0 - Added better errorhandling and support for HTTP Basic Authentication
14.0.1.0.0 - Initial version
    """,
    "category": "REST",
    "version": "14.0.1.3.0",
    "depends": [
        "base",
    ],
    "data": [
        "views/rest_base_view.xml",
        "views/rest_log_view.xml",
        "views/rest_api_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/ir_actions_server.xml",
        "demo/rest_api_data.xml",
    ],
    "installable": True,
    "application": False,
    "author": "Vertel AB",
    "website": "www.vertel.se",
}
