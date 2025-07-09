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
import shutil
import tempfile
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


class IrAttachment(orm.Model):
    """ Model name: IrAttachment
    """
    _inherit = 'ir.attachment'

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    def _get_php_return_page(self, cr, uid, fullname, name, context=None):
        """ Generate return object for pased files
        """
        config_pool = self.pool.get('ir.config_parameter')
        key = 'web.base.url.docnaet'
        config_ids = config_pool.search(cr, uid, [
            ('key', '=', key),
        ], context=context)
        if not config_ids:
            raise osv.except_osv(
                _('Errore'),
                _('Avvisare amministratore: configurare parametro: %s' % key),
                )
        config_proxy = config_pool.browse(cr, uid, config_ids, context=context)[0]
        base_address = config_proxy.value
        _logger.info('URL parameter: %s' % base_address)

        return {
            'type': 'ir.actions.act_url',
            'url': '%s/save_as.php?filename=%s&name=%s' % (
                base_address,
                fullname,
                name
                ),
            # 'target': 'new',
            }

    def return_attachment_apache_php(self, cr, uid, ids, context=None):
        """ Return attachment passed
        """
        # TODO save attachment in temp folder and return
        return True

    def return_file_apache_php(
            self, cr, uid, origin, name=False, context=None):
        """ Return file passed as fullpath name, also passed name of file
            for client
        """
        # Generate a temp filename:
        tmp = tempfile.NamedTemporaryFile()
        extension = origin.split('.')[-1]
        if len(extension) > 6:  # XXX max estension length
            extension = ''
        destination = '%s.%s' % (tmp.name, extension)
        tmp.close()

        # Copy current file in temp destination
        try:
            shutil.copyfile(origin, destination)
        except:
            raise osv.except_osv(
                _('File non trovato'),
                _(u'File non trovato nella gest. documentale!\n%s' % origin),
                )

        if not name:
            name = 'docnaet_download.%s' % extension

        # Return link for open temp file:
        return self._get_php_return_page(cr, uid, destination, name, context=context)
