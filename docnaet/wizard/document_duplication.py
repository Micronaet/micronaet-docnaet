# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import logging
import shutil
from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.tools.translate import _
from odoo import exceptions

_logger = logging.getLogger(__name__)


class DocumentDuplication(models.TransientModel):
    """ Wizard for duplicate model
    """
    _name = 'docnaet.document.duplication.wizard'
    _description = 'Document duplication'

    @api.model
    def duplicate_operation(self, mode='link'):
        """ Manage 2 case
        """
        self.ensure_one()
        if self.env.context is None:
            raise exceptions.Warning(
                _('Cannot found original document'),
                )

        # Pool used:
        document_pool = self.pool.get('docnaet.document')
        protocol_pool = self.pool.get('docnaet.protocol')

        # with_number = context.get('with_number', False)
        linked_document = self.env.context.get('linked_document', False)

        # Record data management:
        original_id = self.env.context.get('active_id')
        original_proxy = document_pool.browse(original_id)
        docnaet_mode = original_proxy.docnaet_mode
        self.env.context['docnaet_mode'] = docnaet_mode
        reassign_protocol = True if self.protocol_id else False
        protocol_id = \
            self.protocol_id.id or original_proxy.protocol_id.id or False

        if docnaet_mode == 'labnaet' and mode != 'link':
            labnaet_id = document_pool.get_counter_labnaet_id()
        else:
            labnaet_id = False

        data = {
            # Labnaet management:
            'docnaet_mode': docnaet_mode,
            'labnaet_id': labnaet_id,

            'name': original_proxy.name,
            'description': original_proxy.description,
            'note': original_proxy.note,
            # 'number': False,
            # 'fax_number': False,
            'date': datetime.now(),
            'deadline': False,
            'deadline_info': False,
            'protocol_id': protocol_id,
            'language_id': original_proxy.language_id.id,
            'type_id': original_proxy.type_id.id,
            'company_id': original_proxy.company_id.id,
            'user_id': self.env.user.id,
            'partner_id': original_proxy.partner_id.id,
            'sector_id': original_proxy.sector_id.id,
            'docnaet_extension': original_proxy.docnaet_extension,
            'program_id': original_proxy.program_id.id,
            'priority': original_proxy.priority,
            'state': 'draft',
            # XXX remember when add new fields to update this record!
            'original_id': original_id if mode == 'link' else False,
            }

        # ---------------------------------------------------------------------
        # Manage protocol number (3 cases):
        # ---------------------------------------------------------------------
        if reassign_protocol or not linked_document:  # always if reassigned
            data['number'] = protocol_pool.assign_protocol_number(protocol_id)
        elif linked_document:  # linked not reassigned keep the number
            data['number'] = original_proxy.number or False
        else:
            data['number'] = False

        destination_proxy = document_pool.create(data)

        # ---------------------------------------------------------------------
        # File management:
        # ---------------------------------------------------------------------
        if mode != 'link':
            # duplicate also file:
            original_file = original_proxy.get_document_filename(
                mode='fullname')
            destination_file = destination_proxy.get_document_filename(
                mode='fullname')
            shutil.copyfile(original_file, destination_file)
            try:
                os.system('chown openerp7:openerp7 %s' % destination_file)
                os.system('chmod 775 %s' % destination_file)
                _logger.info('Change permission to new file')
            except:
                _logger.error('Cannot set property of file')

        return {
            'view_type': 'form',
            'view_mode': 'form,tree,calendar',
            'res_model': 'docnaet.document',
            'domain': [('id', '=', destination_proxy.id)],
            'type': 'ir.actions.act_window',
            'res_id': destination_proxy.id,  # IDs selected
            }

    @api.multi
    def duplication_document(self):
        """ Duplicate document and file
        """
        return self.duplicate_operation(mode='document')

    @api.multi
    def linked_document(self):
        """ Duplicate record but not file
        """
        self.env.context['linked_document'] = True
        return self.duplicate_operation(mode='link')

    protocol_id = fields.Many2one('docnaet.protocol', 'Protocol')
    docnaet_mode = fields.Selection([
        ('docnaet', 'Docnaet'),  # Only for docnaet
        ('labnaet', 'Labnaet'),
        ], 'Docnaet mode', required=True,
        help='Usually document management, but for future improvement also'
             ' for manage other docs')
