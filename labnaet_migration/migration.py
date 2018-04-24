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
from openerp import SUPERUSER_ID#, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class ResPartner(orm.Model):
    ''' Add extra fields for partner migration
    '''
    _inherit = 'res.partner'
    
    _columns = {
        'labnaet_id': fields.integer('Labnaet ID migration'), 
        }
    
class ProductProductDocnaet(orm.Model):
    ''' Object product.product.docnaet
    '''    
    _inherit = 'product.product.docnaet'
                    
    _columns = {        
        'docnaet_id': fields.integer('Docnaet ID migration'),         
        }

class DocnaetProduct(orm.Model):
    """ Model name: Docnaet product
    """    
    _inherit = 'docnaet.product'

    _columns = {        
        'docnaet_id': fields.integer('Docnaet ID migration'),         
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
