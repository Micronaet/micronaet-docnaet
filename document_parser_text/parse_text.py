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

# Parse library:
from subprocess import Popen, PIPE
from docx import opendocx, getdocumenttext
#http://stackoverflow.com/questions/5725278/python-help-using-pdfminer-as-a-library
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO


_logger = logging.getLogger(__name__)

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
        
        # Check file type from extension: 
        extension = self.get_file_extension(filename)
           
        if extension == 'doc':
            cmd = ['antiword', fullname]
            p = Popen(cmd, stdout=PIPE)
            stdout, stderr = p.communicate()
            return stdout.decode('ascii', 'ignore')
        elif extension == 'docx':
            document = opendocx(fullname)
            paratextlist = getdocumenttext(document)
            newparatextlist = []
            for paratext in paratextlist:
                newparatextlist.append(paratext.encode('utf-8'))
            return '\n\n'.join(newparatextlist)
        elif extension == 'odt':
            cmd = ['odt2txt', fullname]
            p = Popen(cmd, stdout=PIPE)
            stdout, stderr = p.communicate()
            return stdout.decode('ascii', 'ignore')
        elif extension == 'pdf':
            return document_parse_pdf_to_txt(fullname)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
