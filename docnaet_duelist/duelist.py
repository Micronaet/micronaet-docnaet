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


class ResPartner(orm.Model):
    """ Model name: ResPartner
    """

    _inherit = 'res.partner'

    def _get_partner_duelist_check(
            self, cr, uid, ids, fields, args,
            context=None):
        """ Fields function for calculate
        """
        res = {}
        now = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        company_cache = {}
        for partner in self.browse(
                cr, uid, ids, context=context):
            company = partner.company_id
            if company in company_cache:
                etl_duelist_file = company_cache[company]
            else:
                etl_duelist_file = company.etl_duelist_file
                company_cache[company] = etl_duelist_file

            res[partner.id] = {}
            res[partner.id]['deadline_present'] = False
            res[partner.id]['deadline_comment'] = False
            res[partner.id]['etl_duelist_file'] = etl_duelist_file

            # This partner payment deadline:
            total_deadlined = 0
            for payment in partner.duelist_ids:
                if payment.deadline < now:  # and payment.total > 0:
                    total_deadlined += payment.total
            if total_deadlined > 0:
                res[partner.id]['deadline_present'] = True
                res[partner.id]['deadline_comment'] = \
                    _('PAGAMENTI SCADUTI! [Agg. %s]' % etl_duelist_file)
                break

            # Parent partner payment deadline:
            total_deadlined = 0
            if partner.docnaet_parent_id:
                for payment in partner.docnaet_parent_id.duelist_ids:
                    if payment.deadline < now:
                        total_deadlined += payment.total

            if total_deadlined > 0:
                res[partner.id]['deadline_present'] = True
                res[partner.id]['deadline_comment'] = \
                    _('PAGAMENTI SCADUTI! [Agg. %s]' % etl_duelist_file)
                break
        return res

    _columns = {
        'deadline_present': fields.function(
            _get_partner_duelist_check, method=True,
            type='boolean', string='Deadline present',
            store=False, multi=True),
        'deadline_comment': fields.function(
            _get_partner_duelist_check, method=True,
            type='char', size=80, string='Deadline comment',
            store=False, multi=True),
        'etl_duelist_file': fields.function(
            _get_partner_duelist_check, method=True,
            type='datetime', string='Aggiornato il',
            store=False, multi=True),
        }


class DocnaetDocument(orm.Model):
    """ Model name: Docnaet Document
    """
    _inherit = 'docnaet.document'

    _columns = {
        'deadline_present': fields.related(
            'partner_id', 'deadline_present',
            type='boolean', string='Deadline present',
            store=False),
        'deadline_comment': fields.related(
            'partner_id', 'deadline_comment',
            type='char', string='Deadline comment',
            store=False),
        'duelist_ids': fields.related(
            'partner_id', 'duelist_ids',
            type='one2many', relation='sql.payment.duelist',
            string='Duelist'),
        }
