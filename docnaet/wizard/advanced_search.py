# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import logging
from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.tools.translate import _
from odoo import exceptions

_logger = logging.getLogger(__name__)


class DocnaetDocumentAdvancedSearchWizard(models.TransientModel):
    """ Wizard for duplicate model
    """
    _name = 'docnaet.document.advanced.search.wizard'
    _description = 'Advanced search'

    # TODO api onchange
    @api.model
    def onchange_country_partner_domain(
            self, partner_name, country_id, category_id):
        """ On change for domain purpose
        """
        partner_pool = self.env['res.partner']
        res = {}
        res['domain'] = {'partner_id': [
            ('docnaet_enable', '=', True),
            ]}

        if partner_name:
            res['domain']['partner_id'].extend([
                ('name', 'ilike', partner_name)
                ])

        if country_id:
            res['domain']['partner_id'].extend([
                ('country_id', '=', country_id)
                ])
        if category_id:
            res['domain']['partner_id'].extend([
                ('docnaet_category_id', '=', category_id)
                ])

        _logger.error('DOMAIN: %s' % (res, ))
        return res

    @api.multi
    def advanced_search(self):
        """ Advanced search
        """
        self.ensure_one()

        # Pool used:
        document_pool = self.env['docnaet.document']
        parent_pool = self.env['res.partner']

        docnaet_mode = self.docnaet_mode or 'docnaet'

        keywords = self.keywords
        partner_name = self.partner_name
        protocol_id = self.protocol_id.id
        sector_id = self.sector_id.id
        partner_id = self.partner_id.id
        country_id = self.country_id.id
        from_date = self.from_date
        to_date = self.to_date
        from_deadline = self.from_deadline
        to_deadline = self.to_deadline

        # Labnaet:
        product_id = self.product_id.id
        docnaet_product_category_id = \
            self.docnaet_product_category_id.id

        name = self.name
        number = self.number
        user_id = self.user_id.id
        description = self.description
        note = self.note
        type_id = self.type_id.id
        language_id = self.language_id.id
        program_id = self.program_id.id
        docnaet_extension = self.docnaet_extension
        priority = self.priority
        docnaet_category_id = self.docnaet_category_id.id

        domain = [('docnaet_mode', '=', docnaet_mode)]

        if partner_name:
            # Search partner name in partner but also in parent name:
            partner_ids = parent_pool.search([
                '|',
                ('name', 'ilike', partner_name),
                ('docnaet_parent_id.name', 'ilike', partner_name),
                ])
            domain.append(('partner_id', 'in', partner_ids))

        if partner_id:
            # Search partner name in partner but also in parent id:
            partner_ids = parent_pool.search([
                ('docnaet_parent_id', '=', partner_id),
                ])
            partner_ids.append(partner_id)
            domain.append(('partner_id', 'in', partner_ids))

        if sector_id:
            domain.append(('sector_id', '=', sector_id))
        if protocol_id:
            domain.append(('protocol_id', '=', protocol_id))
        if country_id:
            domain.append(('country_id', '=', country_id))

        # Labnaet:
        if product_id:
            domain.append(('product_id', '=', product_id))
        if docnaet_product_category_id:
            domain.append(
                ('docnaet_product_category_id', '=',
                    docnaet_product_category_id))

        if from_date:
            domain.append(('date', '>=', from_date))
        if to_date:
            domain.append(('date', '<=', from_date))

        if from_deadline:
            domain.append(('deadline', '>=', from_deadline))
        if to_deadline:
            domain.append(('deadline', '<=', to_deadline))

        if name:
            domain.append(('name', 'ilike', name))
        if number:
            domain.append(('number', 'ilike', number))
        if user_id:
            domain.append(('user_id', '=', user_id))
        if description:
            domain.append(('description', 'ilike', description))
        if note:
            domain.append(('note', 'ilike', note))
        if type_id:
            domain.append(('type_id', '=', type_id))
        if language_id:
            domain.append(('language_id', '=', language_id))
        if program_id:
            domain.append(('program_id', '=', program_id))
        if docnaet_extension:
            domain.append(('docnaet_extension', 'ilike', docnaet_extension))
        if priority:
            domain.append(('priority', '=', priority))
        if docnaet_category_id:
            domain.append(('docnaet_category_id', '=', docnaet_category_id))

        # Multi search management of split keywords:
        if keywords:
            set_ids = {}
            for field in ('name', 'note', 'description'):
                kw_domain = []
                for key in keywords.split():
                    kw_domain.append((field, 'ilike', key))
                set_ids[field] = set(document_pool.search(kw_domain))
            keyword_ids = list(
                set_ids['name'] | set_ids['note'] | set_ids['description'])
            domain.append(('id', 'in', keyword_ids))

        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': domain,
            'type': 'ir.actions.act_window',
            # 'res_id': destination_id,  # IDs selected
            'context': self.env.context,
            }

    keywords = fields.Char('Keywords', size=80)
    partner_name = fields.Char('Partner name', size=80)
    protocol_id = fields.Many2one(
        'docnaet.protocol', 'Protocol',
        domain=[('invisible', '=', False)])
    partner_id = fields.Many2one('res.partner', 'Partner')
    sector_id = fields.Many2one('docnaet.sector', 'Settore')
    # 'docnaet_parent_id = fields.Many2one('res.partner', 'Parent partner')
    country_id = fields.Many2one('res.country', 'Country')
    from_date = fields.Date('From date')
    to_date = fields.Date('To date')
    from_deadline = fields.Date('From deadline')
    to_deadline = fields.Date('To deadline')
    name = fields.Char('Subject', size=180)
    user_id = fields.Many2one('res.users', 'User')
    description = fields.Char('Description', size=180,)
    note = fields.Char('Note', size=180,)
    type_id = fields.Many2one(
        'docnaet.type', 'Type',
        domain=[('invisible', '=', False)])
    number = fields.Char('N.', size=10),
    language_id = fields.Many2one('docnaet.language', 'Language')
    program_id = fields.Many2one(
        'docnaet.protocol.template.program', 'Type of document')
    docnaet_extension = fields.Char('Ext.', size=10)
    docnaet_category_id = fields.Many2one(
        'res.partner.docnaet', 'Partner category',
        )
    # Labnaet:
    product_id = fields.Many2one(
        'docnaet.product', 'Product'),
    docnaet_product_category_id = fields.Many2one(
        'product.product.docnaet', 'Product category',
        )

    priority = fields.Selection([
        ('lowest', 'Lowest'),
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'high'),
        ('highest', 'Highest'),
        ], 'Priority')
    docnaet_mode = fields.Selection([
        ('docnaet', 'Docnaet'),  # Only for docnaet
        ('labnaet', 'Labnaet'),
        ], 'Docnaet mode', required=True, default='docnaet',
        help='Usually document management, but for future improvement also'
             ' for manage other docs')

