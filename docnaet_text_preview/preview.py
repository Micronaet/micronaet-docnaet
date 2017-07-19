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

# -----------------------------------------------------------------------------
# Parse library:
# -----------------------------------------------------------------------------
# Lauch in shell:
from subprocess import Popen, PIPE
# Install: antiword, odt2txt
from cStringIO import StringIO

# DocX:
try:
    from docx import opendocx, getdocumenttext
except:
    _logger('DocX converter not found!')

# PDF:
#http://stackoverflow.com/questions/5725278/\
#python-help-using-pdfminer-as-a-library
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

# EML:
import email
import os


class ResCompany(orm.Model):
    """ Model name: ResCompany
    """    
    _inherit = 'res.company'
    
    # -------------------------------------------------------------------------
    # Utility function for parse text:
    # -------------------------------------------------------------------------
    def get_file_extension(self, filename):
        ''' Return file extension
        '''
        file_list = filename.split('.')
        if len(file_list) <= 1:
            return ''
        return file_list[-1].lower()
        
    def document_parse_doc_to_text(self, filename, fullname):
        ''' Convert utility for docx, doc, pdf, odt document
        '''
        # ---------------------------------------------------------------------
        # Utility for PDF:
        # ---------------------------------------------------------------------
        def document_parse_pdf_to_txt(fullname):
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            codec = 'utf-8'
            laparams = LAParams()
            device = TextConverter(
                rsrcmgr, retstr, codec=codec, laparams=laparams)
            fp = file(fullname, 'rb')
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ''
            maxpages = 0
            caching = True
            pagenos=set()
            for page in PDFPage.get_pages(
                    fp, pagenos, maxpages=maxpages, password=password, 
                    caching=caching, check_extractable=True):
                interpreter.process_page(page)
            fp.close()
            device.close()
            str = retstr.getvalue()
            retstr.close()
            return str

        # ---------------------------------------------------------------------
        # Utility for EML:
        # ---------------------------------------------------------------------
        '''def extract (msgfile, key):
            """ 
            Extracts all data from e-mail, including From, To, etc., and 
            returns it as a dictionary.
            msgfile -- A file-like readable object
            key     -- Some ID string for that particular Message. Can be a 
                file name or anything.
            Returns dict()
            Keys: from, to, subject, date, text, html, parts[, files]
            Key files will be present only when message contained binary files.
            For more see __doc__ for pullout() and caption() functions.
            """
            m = message_from_file(msgfile)
            From, To, Subject, Date = caption(m)
            Text, Html, Files, Parts = pullout(m, key)
            Text = Text.strip(); Html = Html.strip()
            msg = {
                'subject': Subject, 
                'from': From, 
                'to': To, 
                'date': Date,
                'text': Text, 
                'html': Html, 
                'parts': Parts,
                }
            if Files: 
                msg['files'] = Files
            return msg

        def caption(origin):
            """
            Extracts: To, From, Subject and Date from email.Message() or 
                mailbox.Message()
            origin -- Message() object
            Returns tuple(From, To, Subject, Date)
            If message doesn't contain one/more of them, the empty strings will
            be returned.
            """
            Date = ''
            if origin.has_key('date'): 
                Date = origin['date'].strip()
            From = ''
            if origin.has_key('from'): 
                From = origin['from'].strip()
            To = ''
            if origin.has_key('to'): 
                To = origin['to'].strip()
            Subject = ''
            if origin.has_key('subject'): 
                Subject = origin['subject'].strip()
            return From, To, Subject, Date '''
            
        # Check file type from extension: 
        extension = self.get_file_extension(filename)
           
        if extension == 'doc':
            try:
                cmd = ['antiword', fullname]
                p = Popen(cmd, stdout=PIPE)
                stdout, stderr = p.communicate()
                return stdout.decode('ascii', 'ignore')
            except:
                _logger.error('Error access file: %s' % filename)
                return ''    
                
        elif extension == 'docx':
            try:
                document = opendocx(fullname)
                paratextlist = getdocumenttext(document)
                newparatextlist = []
                for paratext in paratextlist:
                    newparatextlist.append(paratext.encode('utf-8'))
                return '\n\n'.join(newparatextlist)
            except:
                return 'Problem read file: %s (or converter not installed)' %\
                    filename    
                    
        elif extension == 'odt':
            cmd = ['odt2txt', '--stdout', fullname]
            p = Popen(cmd, stdout=PIPE)
            stdout, stderr = p.communicate()
            return stdout.decode('ascii', 'ignore')
            
        elif extension == 'eml':
            #f = open(fullname, 'rb')
            #res = '%s' % (extract(f, f.name), )
            #f.close()
            #return res

            f = open(fullname)
            msg = email.message_from_file(f)
            #attachments = msg.get_payload()
            #for attachment in attachments:
            #    try:
            #        fnam=attachment.get_filename()
            #        f = open(fnam, 'wb').write(attachment.get_payload(decode=True,))
            #        f.close()
            #    except Exception as detail:
            #        #print detail
            #        pass            
            data = {
                'Return-Path': '',
                'Delivered-To': '', 
                'Received': '',
                'Delivered-To': '', 
                'Received': '',
                'Date': '',
                'Message-ID': '',
                'From': '',
                'To': '',
                #'X-Originating-IP': '',
                #'X-Qmail-Scanner-Diagnostics': '',
                #'X-Spam-Status': '',
                #'Received-SPF': '',
                #'DKIM-Signature': '',
                #'X-Google-DKIM-Signature': '',
                #'X-Gm-Message-State': '',
                #'X-Received': '',
                #'MIME-Version': '',
                'References': '',
                'In-Reply-To': '', 
                'Subject': '',
                'Content-Type': '',
                }

            for key, value in msg.items():
                if key not in data:
                    continue
                data[key] += value
            return _('''
                Date: %(Date)s\n
                From: %(From)s To: %(Delivered-To)s\n
                Subject: %(Subject)s\n
                Content: %(Content-Type)s\n                
                ''') % data                
            
        elif extension == 'pdf':
            return document_parse_pdf_to_txt(fullname)
            
class DocnaetDocument(orm.Model):
    """ Model name: DocnaetDocument
    """
    
    _inherit = 'docnaet.document'
    
    def document_text_preview(self, cr, uid, ids, context=None):
        ''' Return document preview
        '''
        model_pool = self.pool.get('ir.model.data')
        view_id = model_pool.get_object_reference(
            cr, uid, 
            'docnaet_text_preview', 
            'view_document_text_preview_form',
            )[1]
    
        return {
            'type': 'ir.actions.act_window',
            'name': _('Text preview'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': ids[0],
            'res_model': 'docnaet.document',
            'view_id': view_id, # False
            'views': [(view_id, 'form')],
            'domain': [],
            'context': context,
            'target': 'new',
            'nodestroy': False,
            }
            
    def _get_text_preview_of_document(
            self, cr, uid, ids, fields, args, context=None):
        ''' Fields function for calculate 
        '''
        company_pool = self.pool.get('res.company')
        res = {}
        for document in self.browse(cr, uid, ids, context=context):
            filename = self.get_document_filename(
                cr, uid, document, mode='filename', context=context)
            fullname = self.get_document_filename(
                cr, uid, document, mode='fullname', context=context)
                
            res[document.id] = company_pool.document_parse_doc_to_text(
                filename, fullname)
        return res
        
    _columns = {
        'text_preview': fields.function(
            _get_text_preview_of_document, method=True, 
            type='text', string='Text preview', 
            store=False),                         
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
