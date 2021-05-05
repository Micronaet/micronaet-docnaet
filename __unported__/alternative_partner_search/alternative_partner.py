#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<https://micronaet.com>)
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


class ResPartner(osv.osv):
    ''' Extra fields for partner
    '''
    _inherit = 'res.partner'

    _columns = {
        'alternative_search': fields.char('Ricerca alternativa', size=64),
        }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, 
            context=None, count=False):
        """ Return a list of integers based on search domain {args}
            @param cr: cursor to database
            @param uid: id of current user
            @param args: list of conditions to be applied in search opertion
            @param offset: default from first record, you can start from n records
            @param limit: number of records to be comes in answer from search opertion
            @param order: ordering on any field(s)
            @param context: context arguments, like lang, time zone
            @param count: 
            
            @return: a list of integers based on search domain
        """
        if args is None:
            args = []
        
        new_args = []
        for record in args:
            if record[0] == 'name':
                new_args.extend([
                    '|', 
                    record, 
                    ('alternative_search', 'ilike', record[2]),
                    ])
            else:
                new_args.append(record)                        
        res = super(ResPartner, self).search(
            cr, uid, new_args, offset, limit, order, context, count)
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', 
            context=None, limit=80):
        """ Return a list of tupples contains id, name, as internally its calls 
            {def name_get}
            result format : {[(id, name), (id, name), ...]}
            
            @param cr: cursor to database
            @param uid: id of current user
            @param name: name to be search 
            @param args: other arguments
            @param operator: default operator is ilike, it can be change
            @param context: context arguments, like lang, time zone
            @param limit: returns first n ids of complete result, default it is 80
            
            @return: return a list of tupples contains id, name
        """
        if args is None:
            args = []
        if context is None:
            context = {}

        ids = []
        if name:
            ids = self.search(cr, uid, [
                '|',
                ('name', 'ilike', name),
                ('alternative_search', 'ilike', name),
                ] + args, limit=limit)
        return self.name_get(cr, uid, ids, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
