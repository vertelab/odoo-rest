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
    "name": "Rest Best",
    "description": """
Implements REST calls to the Best API.
See more at https://www.besttransport.se/foretag/leveransomr%C3%A5desapi/
14.0.0.0.0 - Initial version
    """,
    "category": "REST",
    "version": "14.0.0.0.0",
    "depends": [
        "rest_base",
        "base",
    ],
    "data": [
        "data/rest_api_data.xml",
        "views/rest_api_view.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "author": "Vertel AB",
    "website": "www.vertel.se",
}
