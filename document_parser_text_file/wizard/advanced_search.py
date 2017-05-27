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


import os
import sys
import logging
import openerp
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)


class FileDocumentAdvancedSearchWizard(orm.TransientModel):
    ''' Wizard for advanced search
    '''
    _name = 'file.document.advanced.search.wizard'

    # --------------------
    # Wizard button event:
    # --------------------
    def action_search(self, cr, uid, ids, context=None):
        ''' Event for button search
        '''
        if context is None: 
            context = {}        
        
        # Read wizard parameters:
        wiz_browse = self.browse(cr, uid, ids, context=context)[0]
        keywords = wiz_browse.keywords
        partner_name = wiz_browse.partner_name
        agent_name = wiz_browse.agent_name
        from_create_date = wiz_browse.from_create_date
        to_create_date = wiz_browse.to_create_date
        from_modify_date = wiz_browse.from_modify_date
        to_modify_date = wiz_browse.to_modify_date
        
        # Complex query search for keywords (not use domain)
        query = '''SELECT id FROM file_document WHERE %s;'''
        where = ''    

        for keyword in keywords.split():
            where += "%scontent ilike '%%%s%%'" % (
                ' AND ' if where else '',
                keyword,
                )
        query = query % where        
        cr.execute(query)
        _logger.info('Run query: %s' % query)

        # Create domain filter:        
        file_ids = [f[0] for f in cr.fetchall()]
        domain = [('id', 'in', file_ids)]
        if partner_name:
            domain.append(('partner_name', 'ilike', partner_name))
        if agent_name:
            domain.append(('agent_name', 'ilike', agent_name))
        if from_create_date:
            domain.append(
                ('file_create', '>=', '%s 00:00:00' % from_create_date))
        if to_create_date:
            domain.append(
                ('file_create', '<=', '%s 23:59:59' % to_create_date))
        if from_modify_date:
            domain.append(
                ('file_modify', '>=', '%s 00:00:00' % from_modify_date))
        if to_modify_date:
            domain.append(
                ('file_modify', '<=', '%s 23:59:59' % to_modify_date))
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Keywords search'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'file.document',
            #'view_id': view_id, # False
            'views': [(False, 'tree'), (False, 'form')],
            'domain': domain,
            'context': context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
        
    _columns = {
        'keywords': fields.char('Keyword', size=180, required=True),
        'partner_name': fields.char('Partner name', size=180),
        'agent_name': fields.char('Agent name', size=180),
        'from_create_date': fields.date('From create date'),
        'to_create_date': fields.date('To create date'),
        'from_modify_date': fields.date('From modify date'),
        'to_modify_date': fields.date('To modify date'),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


