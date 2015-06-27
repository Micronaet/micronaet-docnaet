# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : 'Docnaet CRM',
    'version' : '0.0.1',
    'category' : 'Generic Modules/Customization',
    'description' : """Interface for manage CRM where information are keep in
                       Docnaet system
                       1. Manage a calendar view for show docnaet documents
                          and deadlines
                       2. Manage a scheduled operation for send mail with 
                          details link for docnaet documents
                    """,
    'author' : 'Micronaet s.r.l.',
    'website' : 'http://www.micronaet.it',
    'depends' : ['base', 
                 'base_calendar',
                 'crm',
                 'docnaet',
                ],
    'init_xml' : [], 
    'update_xml' : [
                    'crm_view.xml',
                    'scheduler.xml',
                    
                    # Template:
                    'data/alert_email.xml',
                   ],
    'demo_xml' : [],
    'active' : False, 
    'installable' : True, 
}
