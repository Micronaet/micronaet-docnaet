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
import shutil
from openerp.osv import osv, orm, fields
from datetime import datetime
from datetime import datetime, timedelta
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class docnaet_import_datasheet_wizard(orm.TransientModel):
    ''' Wizard for import datasheet
    '''
    _name = 'docnaet.import.datasheet.wizard'
    _description = 'Import datasheet'

    def import_operation(self, cr, uid, ids, context=None):
        ''' Import management
        '''
        assert len(ids) == 1, 'Works only with one record a time'
            
        wiz_proxy = self.browse(cr, uid, ids, context=context)[0]
            
        # Pool used:
        document_pool = self.pool.get('docnaet.document')
        protocol_pool = self.pool.get('docnaet.protocol')
        
    _columns = {
        'default_path': fields.char('Default path', size=180, required=True),
        'filename': fields.char('File name', size=180, required=True),
        }

