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
    'name': 'Docnaet',
    'version': '0.0.1',
    'category': 'Document Management',
    'description': '''
        Micronaet - Docnaet Document Manager
        Default module for create structure to integrare Docnaet Management    
        ''',
    'author': 'Micronaet s.r.l.',
    'website': 'http://www.micronaet.it',
    'depends': [
        'base',   
        #'product',
        #'web_m2o_enhanced', # XXX not work if enabled!
        ],
    'init_xml': [], 
    'data': [
        'security/docnaet_group.xml',
        'security/ir.model.access.csv',

        'data/config.xml',
        'data/counter.xml',

        'wizard/document_duplication_view.xml',
        'docnaet_view.xml',
        'docnaet_workflow.xml',

        'wizard/search_view.xml',
        ],
    'demo_xml': [],
    'active': False, 
    'installable': True, 
    #'application': True,
    }
