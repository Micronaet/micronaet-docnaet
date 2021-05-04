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


class ResCompany(models.Model):
    """ Docnaet company extra fields
    """
    _inherit = 'res.company'

    @api.model
    def get_docnaet_folder_path(self, subfolder='root'):
        """ Function for get (or create) root docnaet folder
            (also create extra subfolder)
            subfolder: string value for sub root folder, valid value:
                > 'store'
                > 'private'
            context: used field_path for read correct path name in company
        """
        if 'docnaet_mode' not in self.env.context:
            _logger.error('No docnaet mode parameter in context!')
        field_path = '%s_path' % self.env.context.get(
            'docnaet_mode', 'docnaet')

        # Get docnaet path from company element
        company_proxy = self.env.user.company_id
        docnaet_path = company_proxy.__getattr__(field_path)  # XXX variable

        # Folder structure:
        path = {}
        path['root'] = docnaet_path
        path['store'] = os.path.join(docnaet_path, 'store')
        path['private'] = os.path.join(docnaet_path, 'private')
        path['user'] = os.path.join(path['private'], str(self.env.user.id))

        # Create folder structure # TODO test if present
        for folder in path:
            if not os.path.isdir(path[folder]):
                os.system('mkdir -p %s' % path[folder])
        return path[subfolder]

    @api.model
    def assign_fax_fax(self):
        """ Assign protocol and update number in record
        """
        company_proxy = self.env.user.company_id
        number = company_proxy.next_fax
        company_proxy.write({
            'next_fax': number + 1,
            })
        return number

    docnaet_path = fields.Char(
        'Docnaet path', size=64, required=True,
        help='Docnaet root path in file system for store docs')
    labnaet_path = fields.Char(
        'Labnaet path', size=64, required=True,
        help='Labnaet root path in file system for store docs')
    next_fax = fields.Integer('Next fax number')


class DocnaetLanguage(models.Model):
    """ Object docnaet.language
    """
    _name = 'docnaet.language'
    _description = 'Docnaet language'
    _order = 'name'

    name = fields.Char(
        'Language', size=64, required=True, translate=True)
    code = fields.Char('Code', size=16)
    iso_code = fields.Char('ISO Code', size=16)
    note = fields.Text('Note')


class ResPartnerDocnaet(models.Model):
    """ Object res.partner.docnaet
    """
    _name = 'res.partner.docnaet'
    _description = 'Partner category'

    name = fields.Char(
        'Docnaet type', size=64, required=True, translate=True)
    note = fields.Text('Note')


class DocnaetSector(models.Model):
    """ Object docnaet.sector
    """
    _name = 'docnaet.sector'
    _description = 'Docnaet sector'

    name = fields.Char(
        'Settore', size=64, required=True, translate=True)
    note = fields.Text('Note')


class ResPartner(models.Model):
    """ Model name: ResPartner
    """
    _inherit = 'res.partner'

    @api.multi
    def set_docnaet_on(self):
        """ Enable docnaet partner
        """
        return self.write({
            'docnaet_enable': True,
            })

    @api.multi
    def set_docnaet_off(self):
        """ Disable docnaet partner
        """
        return self.write({
            'docnaet_enable': False,
            })

    docnaet_parent_id = fields.Many2one(
        'res.partner', 'Docnaet parent partner',
        help='Master partner also searchable')
    docnaet_enable = fields.Boolean('Docnaet partner')
    docnaet_category_id = fields.Many2one(
        'res.partner.docnaet', 'Docnaet category')


class ResPartnerRelation(models.Model):
    """ Model name: ResPartner
    """
    _inherit = 'res.partner'

    docnaet_child_ids = fields.One2many(
        'res.partner', 'docnaet_parent_id', 'Docnaet Ditte Collegate')
    alternative_search = fields.Char('Nome alternativo Docnaet', size=64)

    @api.multi
    def name_get(self):
        """ Add customer-fabric ID to name
        """
        name_mode = self.env.context.get('name_mode')

        res = []
        for partner in self:
            if name_mode == 'docnaet' and partner.alternative_search:
                res.append((partner.id, partner.alternative_search))
            else:
                res.append((partner.id, partner.name))
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ Return a list of integers based on search domain {args}
            @param args: list of conditions to be applied in search opertion
            @param offset: default from first record, you can start from n records
            @param limit: number of records to be comes in answer from search opertion
            @param order: ordering on any field(s)
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

        return super(ResPartner, self).search(
            new_args, offset, limit, order, count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        """ Return a list of tuples contains id, name, as internally its calls
            {def name_get}
            result format : {[(id, name), (id, name), ...]}

            @param name: name to be search
            @param args: other arguments
            @param operator: default operator is ilike, it can be change
            @param limit: returns first n ids of complete result, default 80

            @return: return a list of tupples contains id, name
        """
        if args is None:
            args = []

        if name:
            ids = self.search([
                ('name', 'ilike', name),
                ] + args, limit=limit)
        else:
            ids = []
        return self.name_get()


class ProductProductDocnaet(models.Model):
    """ Object product.product.docnaet
    """
    _name = 'product.product.docnaet'
    _description = 'Product category'

    name = fields.Char(
        'Docnaet category', size=64, required=True, translate=True)
    note = fields.Text('Note')


class DocnaetProduct(models.Model):
    """ Model name: Docnaet product
    """
    _name = 'docnaet.product'
    _description = 'Docnaet Product'

    name = fields.Char(
        'Name', size=64, required=True, translate=True)
    default_code = fields.Char('Default code', size=64)
    docnaet_category_id = fields.Many2one(
        'product.product.docnaet', 'Docnaet category')
    partner_id = fields.Many2one('res.partner', 'Partner')
    note = fields.Text('Note')


class DocnaetType(models.Model):
    """ Object docnaet.type
    """
    _name = 'docnaet.type'
    _description = 'Docnaet type'
    _order = 'name'

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def set_invisibile(self):
        """ Set as invisible protocol
        """
        return self.write({
            'invisible': True,
            })

    @api.multi
    def set_visibile(self):
        """ Set as invisible protocol
        """
        return self.write({
            'invisible': False,
            })

    name = fields.Char('Type', size=64, required=True, translate=True)
    invisible = fields.Boolean('Not used')
    note = fields.Text('Note')
    docnaet_mode = fields.Selection([
        ('docnaet', 'Docnaet'),  # Only for docnaet
        ('labnaet', 'Labnaet'),
        ('all', 'All'),
        ], 'Docnaet mode', required=True, default='docnaet',
        help='Usually document management, but for future improvement also'
             ' for manage other docs')


class DocnaetProtocol(models.Model):
    """ Object docnaet.protocol
    """
    _name = 'docnaet.protocol'
    _description = 'Docnaet protocol'
    _order = 'name'

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def set_invisibile(self):
        """ Set as invisible protocol
        """
        return self.write({
            'invisible': True,
            })

    @api.multi
    def set_visibile(self):
        """ Set as invisible protocol
        """
        return self.write({
            'invisible': False,
            })

    @api.model
    def assign_protocol_number(self, protocol_id):
        """ Assign protocol and update number in record
        """

        protocol_proxy = self.browse(protocol_id)
        number = protocol_proxy.next
        protocol_proxy.write({
            'next': number + 1,
            })
        return number

    name = fields.Char(
        'Protocol', size=64, required=True, translate=True)
    next = fields.Integer('Next protocol', required=True, default=1)
    note = fields.Text('Note', translate=True)
    invisible = fields.Boolean('Not used')
    docnaet_mode = fields.Selection([
        ('docnaet', 'Docnaet'),  # Only for docnaet
        ('labnaet', 'Labnaet'),
        ], 'Docnaet mode', required=True, default='docnaet',
        help='Usually document management, but for future improvement also'
             ' for manage other docs')


class DocnaetProtocolTemplateProgram(models.Model):
    """ Object docnaet.protocol.template.program
    """

    _name = 'docnaet.protocol.template.program'
    _description = 'Docnaet program'
    _order = 'name'

    @api.model
    def get_program_from_extension(self, extension):
        """ Return program ID from extension
        """
        programs = self.search([
            ('extension', 'ilike', extension)
            ])

        if programs:
            return programs[0].id
        else:
            return False

    name = fields.Char('Program', size=64, required=True, translate=True)
    extension = fields.Char('Extension', size=5)
    note = fields.Text('Note', translate=True)


class DocnaetProtocolTemplate(models.Model):
    """ Object docnaet.protocol.template
    """
    _name = 'docnaet.protocol.template'
    _description = 'Docnaet protocol template'
    _rec_name = 'lang_id'
    _order = 'lang_id'

    lang_id = fields.Many2one(
        'docnaet.language', 'Language', required=True)
    protocol_id = fields.Many2one('docnaet.protocol', 'Protocol')
    program_id = fields.Many2one(
        'docnaet.protocol.template.program', 'Program')
    note = fields.Text('Note')


class DocnaetProtocol(models.Model):
    """ 2many fields
    """
    _inherit = 'docnaet.protocol'

    template_ids = fields.One2many(
        'docnaet.protocol.template', 'protocol_id', 'Template'),


class DocnaetDocument(models.Model):
    """ Object docnaet.document
    """
    _name = 'docnaet.document'
    _description = 'Docnaet document'
    _order = 'date desc,number desc'

    # -------------------------------------------------------------------------
    # Onchange event:
    # -------------------------------------------------------------------------
    @api.model
    def onchange_country_partner_domain(
            self, search_partner_name, search_country_id):
        """ On change for domain purpose
        """
        res = {}
        res['domain'] = {'partner_id': [
            ('docnaet_enable', '=', True),
            ]}

        if search_country_id:
            res['domain']['partner_id'].append(
                ('country_id', '=', search_country_id),
                )
        if search_partner_name:
            if '+' in search_partner_name:
                partner_part = search_partner_name.split('+')
                # Add or:
                # res['domain']['partner_id'].extend([
                #    '|' for item in range(1, len(partner_part))])
                # Add partner list of ilike search:
                res['domain']['partner_id'].extend([
                    ('name', 'ilike', p) for p in partner_part])
            else:
                res['domain']['partner_id'].append(
                    ('name', 'ilike', search_partner_name),
                    )
        # if category_id:
        #    res['domain']['partner_id'].append(
        #        ('docnaet_category_id','=', category_id),
        #        )
        _logger.warning('Filter: %s' % res)
        return res

    # -------------------------------------------------------------------------
    # Workflow state event:
    # -------------------------------------------------------------------------
    @api.multi
    def document_draft(self):
        """ WF draft state
        """
        self.ensure_one()
        return self.write({
            'state': 'draft',
            })

    @api.multi
    def document_confirmed(self,):
        """ WF confirmed state
        """
        self.ensure_one()
        data = {'state': 'confirmed'}

        protocol_pool = self.env['docnaet.protocol']
        if not self.number:
            protocol = self.protocol_id
            if not protocol:
                raise exceptions.Warning(
                    _('No protocol assigned, choose one before and confirm!'),
                    )
            if not self.partner_id:
                raise exceptions.Warning(
                    _('No partner assigned, choose one before and confirm!'),
                    )
            data['number'] = protocol_pool.assign_protocol_number(
                protocol.id)
        return self.write(data)

    @api.multi
    def document_suspended(self):
        """ WF suspended state
        """
        return self.write({'state': 'suspended'})

    @api.multi
    def document_timed(self):
        """ WF timed state
        """
        self.ensure_one()

        if not self.deadline:
            raise exceptions.Warning(_('For timed document need a deadline!'))
        return self.write({'state': 'timed'})

    @api.multi
    def document_cancel(self):
        """ WF cancel state
        """
        self.ensure_one()
        return self.write({'state': 'cancel'})

    # -------------------------------------------------------------------------
    # Utility:
    # -------------------------------------------------------------------------
    @api.multi
    def dummy(self):
        return True

    @api.model
    def call_docnaet_url(self, mode, remote=False):
        """ Call url in format: openerp://operation|argument
            Cases:
            document|document_id.extension > open document
            folder|uid > open personal folder (for updload document)

            NOTE: maybe expand the services
        """
        handle = 'openerp'  # TODO put in company as parameter
        doc_proxy = self.browse(cr, uid, ids, context=context)[0]

        # ---------------------------------------------------------------------
        # Labnaet mode:
        # ---------------------------------------------------------------------
        if doc_proxy.docnaet_mode == 'labnaet':
            app = '[L]'
            docnaet_mode = 'labnaet'
        else:
            app = '' # TODO '[D]'
            docnaet_mode = 'docnaet'

        # ---------------------------------------------------------------------
        #                           Operations
        # ---------------------------------------------------------------------
        # A. Open document:
        if mode == 'open':
            filename = self.get_document_filename(
                cr, uid, doc_proxy, mode='filename', context=context)
            final_url = r'%s://document|%s%s' % (
                handle, filename, app)

        # B. Open private folder:
        elif mode == 'home':
            final_url = r'%s://folder|%s%s' % (
                handle, uid, app)

        # C. Open remote document:
        # if remote:
        #    final_url = '%s[R]' % final_url

        return {
            'name': 'Open %s document' % docnaet_mode,
            # res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'url': final_url,
            'target': 'self',
            }

    # -------------------------------------------------------------------------
    # Button event:
    # -------------------------------------------------------------------------
    @api.multi
    def assign_protocol_number(self):
        """ Reassign protocol number (enabled only if protocol and number
            is present (in view)
            Used also for N records
        """
        for document in self:
            number = self.env['docnaet.protocol'].assign_protocol_number(
                document.protocol_id.id)
            document.write({
                'number': number,
                })
        return True

    @api.multi
    def button_doc_info_docnaet(self):
        """ Document info
        """
        self.ensure_one()
        filename = self.get_document_filename(mode='fullname')
        message = _(
            'ID: %s\nOrigin ID: %s\nExtension: %s\n'
            'Old filename: %s\nDocument: %s') % (
                self.id,
                self.original_id.id if
                self.original_id else '',
                self.docnaet_extension or '',
                self.filename or '',
                filename or '',
                )

        raise exceptions.Warning(message)

    @api.multi
    def button_assign_fax_number(self):
        """ Assign fax number to document (next counter)
        """
        if self.fax_number:
            raise exceptions.Warning(_('Fax yet present!'))
        number = self.env['res.company'].assign_fax_fax()
        return self.write({
            'fax_number': number,
            })

    @api.multi
    def button_call_url_docnaet(self):
        """ Call url function for prepare address and return for open doc:
        """
        return self.call_docnaet_url('open')

    @api.multi
    def button_call_url_remote_docnaet(self):
        """ Call url function for prepare address and return for open doc:
            (in remote mode)
        """
        return self.call_docnaet_url('open', remote=True)

    @api.model
    def get_document_filename(self, document, mode='fullname'):
        """ Recursive function for get filename
            document: browse obj
            mode: fullname or filename only
        """
        self.env.context['docnaet_mode'] = document.docnaet_mode

        # 2 different ID:
        if document.docnaet_mode == 'labnaet':
            document_id = document.labnaet_id
        else:  # 'docnaet':
            document_id = document.id

        company_pool = self.env['res.company']
        if document.filename:
            store_folder = company_pool.get_docnaet_folder_path(
                subfolder='store')
            filename = '%s.%s' % (
                document.filename,
                document.docnaet_extension,
                )
            if mode == 'filename':
                return filename
            else:  # fullname:
                return os.path.join(store_folder, filename)
        elif document.original_id:
            return self.get_document_filename(
                cr, uid, document.original_id, mode=mode, context=context)
        else:  # Duplicate also file:
            store_folder = company_pool.get_docnaet_folder_path(
                cr, uid, subfolder='store', context=context)
            filename = '%s.%s' % (document_id, document.docnaet_extension)
            if mode == 'filename':
                return filename
            else:  # fullname mode:
                return os.path.join(store_folder, filename)

    '''
    @api.multi
    def _refresh_partner_country_change(self):
        """ When change partner in country change in document
        """
        return self.env['docnaet.document'].search([
            ('partner_id', 'in', self.mapped['id']),
        ])

    @api.multi
    def _refresh_partner_category_change(self):
        """ When change partner in category change in document
        """
        return self.env['docnaet.document'].search([
            ('partner_id', 'in', self.mapped['id']),
        ])

    @api.multi
    def _refresh_product_category_change(self):
        """ When change product category update docnaet document
        """
        return self.env['docnaet.document'].search([
            ('product_id', 'in', self.mapped['id']),
        ])
    "@api.multi
    def _refresh_category_auto_change(self):
        """ When change partner in category change in document
            Used also for change product_id for update category
        """
        return self.mapped['id']

    @api.multi
    def _refresh_country_auto_change(self):
        """ When change partner in category change in document
        """
        return self.mapped['id']
    '''

    @api.multi
    def _get_real_filename(self):
        """ Fields function for calculate
        """
        for doc in self:
            doc.real_file = doc.filename or doc.original_id.id or ''

    @api.multi
    def _get_date_month_4_group(self):
        """ Fields function for calculate
        """
        for doc in self:
            if doc.date:
                doc.date_month = ('%s' % doc.date)[:7]
            else:
                doc.date_month = _('Nessuna')

    @api.multi
    def _get_deadline_month_4_group(self):
        """ Fields function for calculate
        """
        for doc in self:
            if doc.deadline:
                doc.deadline_month = ('%s' % doc.deadline)[:7]
            else:
                doc.deadline_month = _('Nessuna')

    '''    
    @api.multi
    def _store_data_deadline_month(self):
        """ if change date reload data
        """
        _logger.warning('Change date_mont depend on date and deadline')
        return ids'''

    @api.multi
    def get_counter_labnaet_id(self):
        """ Return ID for labnaet_id
        """
        return int(self.env['ir.sequence'].get(
            'docnaet.document.labnaet'))

    name = fields.Char('Subject', size=180, required=True),
    labnaet_id = fields.Integer(
        'Labnaet ID',
        help='Secondary ID for document, keep data in different folder.')
    filename = fields.Char('File name', size=200)
    real_file = fields.Char(
        compute='_get_real_filename', method=True, size=20,
        string='Real filename')
    description = fields.Text('Description')
    note = fields.Text('Note')

    number = fields.Char('N.', size=10)
    fax_number = fields.Char('Fax n.', size=10)

    date = fields.date('Date', required=True, default=fields.Datetime.now())
    date_month = fields.Char(
        compute='_get_date_month_4_group', method=True,
        string='Mese inser.', size=15,
        # 'docnaet.document' _store_data_deadline_month, ['date']
        )

    deadline_info = fields.Char('Deadline info', size=64),
    deadline = fields.date('Deadline')
    deadline_month = fields.Char(
        compute='_get_deadline_month_4_group', method=True,
        string='Scadenza', size=15,
        # 'docnaet.document': _store_data_deadline_month, ['deadline']
    )

    # OpenERP many2one
    protocol_id = fields.Many2one(
        'docnaet.protocol', 'Protocol',
        domain=[('invisible', '=', False)],
        )
    sector_id = fields.Many2one('docnaet.sector', 'Settore')
    language_id = fields.Many2one('docnaet.language', 'Language')
    type_id = fields.Many2one(
        'docnaet.type', 'Type',
        domain=[('invisible', '=', False)])
    company_id = fields.Many2one('res.company', 'Company')
    user_id = fields.Many2one('res.users', 'User', required=True)

    # Partner:
    partner_id = fields.Many2one('res.partner', 'Partner')
    country_id = fields.Many2one(
        'res.country', related='partner_id.country_id', string='Country',
        # 'res.partner': _refresh_partner_country_change, ['country_id'], 10),
        # 'docnaet.document': _refresh_country_auto_change, ['partner_id'], 10)
    )
    docnaet_category_id = fields.Many2one(
        'res.partner.docnaet', 'partner_id.docnaet_category_id',
        string='Partner category',
        # 'res.partner': _refresh_partner_category_change, 'docnaet_category_id
        # 'docnaet.document': _refresh_category_auto_change, ['partner_id']
    )

    # Product:
    product_id = fields.Many2one('docnaet.product', 'Product')
    docnaet_product_category_id = fields.Many2one(
        'product.product.docnaet', related='product_id.docnaet_category_id',
        string='Product category',
        # 'docnaet.product _refresh_product_category_change docnaet_category_id
        # 'docnaet.document _refresh_category_auto_change, ['product_id']
    )

    # Search partner extra fields:
    search_partner_name = fields.Char(
        'Search per Partner name', size=80)
    search_country_id = fields.Many2one(
        'res.country', 'Search per Country')

    docnaet_extension = fields.Char('Ext.', size=10)
    program_id = fields.Many2one(
        'docnaet.protocol.template.program', 'Type of document')

    original_id = fields.Many2one(
        'docnaet.document', 'Original',
        help='Parent orignal document after this duplication')
    imported = fields.Boolean('Imported')
    private = fields.Boolean('Private')
    docnaet_mode = fields.Selection([
        ('docnaet', 'Docnaet'),  # Only for docnaet
        ('labnaet', 'Labnaet'),
        # ('all', 'All'),
        ], 'Docnaet mode', required=True, default='docnaet',
        help='Usually document management, but for future improvement also'
             ' for manage other docs')

    priority = fields.Selection([
        ('lowest', 'Lowest'),
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'high'),
        ('highest', 'Highest'),
        ], 'Priority', default='normal')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('timed', 'Timed'),
        ('cancel', 'Cancel'),
        ], 'State', readonly=True, default='draft')


class DocnaetDocumentRelations(models.Model):
    """ Add extra relation fields
    """
    _inherit = 'docnaet.document'

    duplicated_ids = fields.One2many(
        'docnaet.document', 'original_id',
        'duplicated', help='Child document duplicated from this')


class ResUsers(models.Model):
    """ Docnaet user extra fields
    """
    _inherit = 'res.users'

    sector_ids = fields.many2many(
        'docnaet.sector', 'docnaet_document_sector_rel',
        'user_id', 'sector_id', 'Settori')
    hide_generic = fields.Boolean(
        'Nascondi generico',
        help='Nasconde i documenti non catalogati per settore')
