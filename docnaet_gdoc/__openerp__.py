# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Docnaet - Gdoc',
    'version': '0.0.1',
    'category': 'Document Management',
    'description': '''
        Integrate G - doc 
        ''',
    'author': 'Micronaet s.r.l.',
    'website': 'http://www.micronaet.it',
    'depends': [
        'base',   
        'docnaet',
        'docnaet_download',
        ],
    'init_xml': [], 
    'data': [
        'gdoc_view.xml',
        ],
    'demo_xml': [],
    'active': False, 
    'installable': True, 
    #'application': True,
    }
