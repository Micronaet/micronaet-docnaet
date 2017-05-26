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
        wiz_browse = self.browse(cr, uid, ids, context=context)[0]
        keywords = wiz_browse.keywords
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
        
        file_ids = [f[0] for f in cr.fetchall()]
        return {
            'type': 'ir.actions.act_window',
            'name': _('Keywords search'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            #'res_id': 1,
            'res_model': 'file.document',
            #'view_id': view_id, # False
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', file_ids)],
            'context': context,
            'target': 'current', # 'new'
            'nodestroy': False,
            }
        
    _columns = {
        'keywords': fields.char('Keyword', size=180, required=True),
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


