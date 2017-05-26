# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class FileDocument(orm.Model):
    """ Model name: FileDocument
    """    
    _name = 'file.document'
    _description = 'File document'
    _rec_name = 'name'
    _order = 'name'
    
    def schedule_load_file_list(
            self, cr, uid, path, doc_filter, context=None):
        ''' Load path passed and create file as record
        '''
        company_pool = self.pool.get('res.company'),
        path = os.path.expanduser(path)

        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in filenames:
                fullname = os.path.join(dirpath, filename)
                content = company_pool.document_parse_doc_to_text
                    (filename, fullname) 
                if not content: 
                    _logger.warning('Empty file: %s' % fullname)
                    continue 
                data = { 
                    'name': filename,
                    'fullname': fullname,
                    'content': content, 
                    }
            
                file_ids = self.search(cr, uid, [
                    ('fullname', '=', fullname), 
                    ], context=context)                 
                if file_ids:
                    self.write(cr, uid, file_ids, data, context=context)
                else:
                    self.create(cr, uid, data, context=context)

                _logger.info('Import: %s' % fullname)
        return True
        
    _columns = {
        'active': fields.boolean('Active'),
        'create_date': fields.date('Create date'),
        'write_date': fields.date('Create date'),
        'name': fields.char(
            'Name', size=80, required=True, readonly=True),
        'fullname': fields.char(
            'Fullname', size=280, required=False, readonly=True),
        'content': fields.text('Content', readonly=True) ,
        }
        
    _defaults = {
        'active', lambda *x: True,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
