# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import logging
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo import exceptions

_logger = logging.getLogger(__name__)


class DocnaetProtocol(models.Model):
    """ Protocol for MRP link
    """
    _inherit = 'docnaet.protocol'

    link_mrp = fields.Boolean('Link', help='Link document in MRP form')


class UploadDocumentWizard(models.TransientModel):
    """ Wizard to upload document
    """
    _name = 'docnaet.document.upload.wizard'
    _description = 'Document upload'

    # TODO change in onchange method:
    @api.model
    def onchange_country_partner_domain(self, partner_name, country_id):
        """ On change for domain purpose
        """
        res = {}
        res['domain'] = {'default_partner_id': [
            ('docnaet_enable', '=', True),
            ]}

        if country_id:
            res['domain']['default_partner_id'].append(
                ('country_id', '=', country_id),
                )
        if partner_name:
            if '+' in partner_name:
                partner_part = partner_name.split('+')
                res['domain']['default_partner_id'].extend([
                    ('name', 'ilike', p) for p in partner_part])
            else:
                res['domain']['default_partner_id'].append(
                    ('name', 'ilike', partner_name),
                    )
        return res

    def private_listdir(self):
        """ Return private listdir list
        """
        res = []

        company_pool = self.env['res.company']
        private_folder = company_pool.get_docnaet_folder_path(
            subfolder='user')

        try:
            listdir = os.listdir(private_folder)
        except:
            raise exceptions.Warning(_('Cannot access: %s' % private_folder))

        for f in listdir:
            try:
                fullpath = os.path.join(private_folder, f)
            except:
                raise exceptions.Warning(
                    _('Change file name, character not permit: %s' % f))
            if not os.path.isfile(fullpath):
                continue
            res.append((fullpath, f))
        return res

    def button_personal_folder(self):
        """ Open personal folder
        """
        # TODO complete open folder with agent procedure
        document_pool = self.env['docnaet.document']
        return document_pool.call_docnaet_url(mode='home')

    def button_reassign(self):
        """ Button reassign wizard
        """
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise exceptions.Warning(_('Select document to reassign'))
        data = {}
        if self.default_partner_id:
            data['partner_id'] = self.default_partner_id.id
        if self.default_user_id:
            data['user_id'] = self.default_user_id.id
        if self.default_protocol_id:
            data['protocol_id'] = self.default_protocol_id.id
        # TODO manage: assign protocol!

        if self.default_type_id:
            data['type_id'] = self.default_type_id.id
        if self.default_language_id:
            data['language_id'] = self.default_language_id.id

        try:
            if self.default_sector_id:
                data['sector_id'] = self.default_sector_id.id
        except:
            pass

        document_pool = self.env['docnaet.document']
        document_pool.browse(active_ids).write(data)

        # Reassign protocol number:
        if self.assign_protocol:
            document_pool.assign_protocol_number(active_ids)
        # TODO reassign_confirm for change status in confirmed

        return {
            'type': 'ir.actions.act_window',
            'name': _('Reassign characteristics'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'docnaet.document',
            'views': [(False, 'tree'), (False, 'form')],
            'domain': [('id', 'in', active_ids)],
            'context': self.env.context,
            'target': 'current',
            'nodestroy': False,
            }

    def button_upload(self):
        """ Button event for upload
        """
        # TODO complete the load from folder:
        wiz_proxy = self
        file_mode = wiz_proxy.file_mode

        # Partial mode
        file_selected = []
        document_imported = []

        if file_mode == 'partial':
            file_selected = [
                item.name for item in wiz_proxy.document_ids if item.to_import]

        company_pool = self.env['res.company']
        document_pool = self.env['docnaet.document']
        protocol_pool = self.env['docnaet.protocol']
        program_pool = self.env['docnaet.protocol.template.program']

        # Difference between Docnaet and Labnaet:
        # TODO? rimuovere?
        # doc_proxy = self.browse(cr, uid, ids, context=context)[0]
        # docnaet_mode = doc_proxy.docnaet_mode
        docnaet_mode = self.docnaet_mode
        if not docnaet_mode:
            raise exceptions.Warning(
                _('Cannot find document mode (labnaet or docnaet'))
        # context['docnaet_mode'] = docnaet_mode

        # ---------------------------------------------------------------------
        # Folder depend on doc/lab mode
        # ---------------------------------------------------------------------
        # Store (output):
        store_folder = company_pool.with_context(docnaet_mode=docnaet_mode).\
            get_docnaet_folder_path(subfolder='store')

        # Private (input):
        private_folder = self.with_context(docnaet_mode=docnaet_mode).\
            private_listdir()

        for fullpath, f in private_folder:
            if file_mode == 'partial' and f not in file_selected:
                continue  # jumped

            # -----------------------------------------------------------------
            # Create record for document:
            # -----------------------------------------------------------------
            extension = f.split('.')[-1].lower()
            real_name = '.'.join(f.split('.')[:-1])  # Remove extension
            if len(extension) > 4:
                _logger.warning(
                    _('Extension must be <= 4 char (jump file %s!') % f)
                continue

            now = fields.Datetime.now()
            data = {
                'name': real_name,
                'docnaet_mode': docnaet_mode,
                'protocol_id': wiz_proxy.default_protocol_id.id or False,
                'user_id': wiz_proxy.default_user_id.id or self.env.user.id,
                'partner_id': wiz_proxy.default_partner_id.id or False,
                'product_id': wiz_proxy.default_product_id.id or False,
                'language_id': wiz_proxy.default_language_id.id or False,
                'sector_id': wiz_proxy.default_sector_id.id or False,

                'type_id': wiz_proxy.default_type_id.id or False,
                'date': now,
                'import_date': now,
                'uploaded': True,
                'docnaet_extension': extension,
                'program_id': program_pool.get_program_from_extension(
                    extension)
                }

            if docnaet_mode == 'labnaet':
                labnaet_id = document_pool.with_context(
                    docnaet_mode=docnaet_mode).get_counter_labnaet_id()
                data.update({
                    'labnaet_id': labnaet_id,
                    })

                # -------------------------------------------------------------
                # TODO Not for general module, remove: MRP Link:
                # -------------------------------------------------------------
                """
                if wiz_proxy.default_protocol_id.link_mrp:
                    mrp_pool = self.env['mrp.production']
                    mrp_name = real_name.replace(' ', '')
                    if len(mrp_name) == 7:
                        mrp_name = '%s/%s' % (mrp_name[:2], mrp_name[2:])
                        mrp_ids = mrp_pool.search([
                            ('name', '=', mrp_name),
                            ])
                        if mrp_ids:
                            real_name = 'Produzione: %s' % mrp_name
                            data.update({
                                'name': real_name,
                                'link_mrp': True,
                                'linked_mrp_id': mrp_ids[0],
                                })
                """
            else:
                labnaet_id = False

            if wiz_proxy.assign_protocol:
                data['number'] = protocol_pool.assign_protocol_number(
                    data['protocol_id'])

            item_id = document_pool.create(data).id
            document_imported.append(item_id)

            # -----------------------------------------------------------------
            # Labnaet alternative:
            # -----------------------------------------------------------------
            # ID mode labnaet / docnaet (force labnaet_id):
            if docnaet_mode == 'labnaet':
                item_id = labnaet_id

            # -----------------------------------------------------------------
            # Import file in store:
            # -----------------------------------------------------------------
            fullstore = '%s.%s' % (
                os.path.join(store_folder, str(item_id)),
                extension,
                )
            os.rename(fullpath, fullstore)

            try:
                os.system('chown openerp7:openerp7 %s' % fullstore)
                os.system('chmod 775 %s' % fullstore)
                _logger.info('Change permission to new file')
            except:
                _logger.error('Cannot set property of file')

        return {
            'view_type': 'form',
            'view_mode': 'tree,form,calendar',
            'res_model': 'docnaet.document',
            'domain': [('id', 'in', document_imported)],
            'type': 'ir.actions.act_window',
            'context': self.with_context(
                default_docnaet_mode=docnaet_mode).env.context,
            }

    @api.model
    def default_read_upload_folder(self, mode='html'):
        """ Read folder and return html text
        """
        docnaet_mode = self.env.context.get('docnaet_mode', 'docnaet')

        if mode == 'html':
            res = ''
        else:
            res = []

        # Get private folder:
        private_folder = self.private_listdir()
        for fullpath, f in private_folder:
            ts = fields.Datetime.fromtimestamp(
                os.path.getmtime(fullpath)).strftime('%Y/%m/%d')
            ts = ts.replace('/', '-')
            if mode == 'html':
                res += '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                    f, ts, f.split('.')[-1])

            else:  # mode default one2many
                res.append((0, 0, {
                    'to_import': False,
                    'name': f,
                    'date': ts,
                    'fullname': fullpath,
                    }))

        if mode == 'html':
            return '''
                    <style>
                        .table_bf {
                             border:1px 
                             padding: 3px;
                             solid black;
                         }
                        .table_bf td {
                             border:1px 
                             solid black;
                             padding: 3px;
                             text-align: center;
                         }
                        .table_bf th {
                             border:1px 
                             solid black;
                             padding: 3px;
                             text-align: center;
                             background-color: grey;
                             color: white;
                         }
                    </style>
                <p> 
                    <table class="table_bf">
                        <tr>
                            <td>&nbsp;Date&nbsp;</td>
                            <td>&nbsp;File name&nbsp;</td>
                            <td>&nbsp;Ext.&nbsp;</td>
                        </tr>
                        %s
                    </table>
                </p>''' % res
        else:
            return res

    mode = fields.Selection([
        ('upload', 'Upload mode'),
        ('reassign', 'Reassign mode'),
        ], 'Mode', default='upload')

    default_sector_id = fields.Many2one('docnaet.sector', 'Settore')

    # Filter for partner:
    partner_name = fields.Char('Partner name', size=80)
    country_id = fields.Many2one('res.country', 'Country')

    default_partner_id = fields.Many2one(
        'res.partner', '>> Default partner',
        domain=[('docnaet_enable', '=', True)],
        )

    # Labnaet:
    default_product_id = fields.Many2one(
        'docnaet.product', 'Product')

    assign_protocol = fields.Boolean(
        'Assign protocol',
        help='In upload mode assign protocol and next number')
    default_user_id = fields.Many2one(
        'res.users', 'User', default=lambda s: s.env.user.id)
    default_protocol_id = fields.Many2one(
        'docnaet.protocol', 'Protocol',
        domain=[('invisible', '=', False)],
        )
    default_type_id = fields.Many2one('docnaet.type', 'Type')
    default_language_id = fields.Many2one('docnaet.language',
        'Language')
    folder_status = fields.Text(
        'Folder status', default=lambda s: s.default_read_upload_folder())
    reassign_confirm = fields.Boolean('Confirm after reassign',
        help='After reassign feature confirm all draft elements')
    file_mode = fields.Selection([
        ('all', 'All'),
        ('partial', 'Partial'),
        ], 'File mode', default='all')
    docnaet_mode = fields.Selection([
        ('docnaet', 'Docnaet'),  # Only for docnaet
        ('labnaet', 'Labnaet'),
        ], 'Docnaet mode', required=True, default='docnaet',
        help='Usually document management, but for future improvement also'
             ' for manage other docs')


class UploadDocumentFile(models.TransientModel):
    """ Wizard to upload document
    """
    _name = 'docnaet.document.upload.file'
    _description = 'Document upload file'

    to_import = fields.Boolean('Import')
    name = fields.Char(
        'File name', size=100, required=True, readonly=True)
    fullname = fields.Char('Full name', size=400)
    date = fields.Date('Time stamp')
    wizard_id = fields.Many2one(
        'docnaet.document.upload.wizard', 'Wizard')


class UploadDocumentWizard(models.TransientModel):
    """ Wizard to upload document
    """
    _inherit = 'docnaet.document.upload.wizard'

    def get_default_file_ids(self):
        """ Load user files directly
        """
        return self.default_read_upload_folder(mode='o2m')

    document_ids = fields.One2many(
        'docnaet.document.upload.file', 'wizard_id', 'Files',
        default=lambda s: s.get_default_file_ids()
    )
