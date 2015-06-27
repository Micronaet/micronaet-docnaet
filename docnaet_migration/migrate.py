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
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

#'docnaet_id': fields.integer('Docnaet ID'),
"""def docnaet_2_openerp_id(self, cr, uid, docnaet_id, context=None):
    ''' Search docnaet ID and return OpenERP ID
    '''
    oerp_id = self.search(cr, uid, [('docnaet_id','=',docnaet_id)])
    if oerp_id:
        return oerp_id[0]
    else:
        return False"""


    # --------------------
    # Utility and function
    # --------------------
    def sync_all_secondary_anagrafic(self, cr, uid, context=None):
        ''' Sinc all secondary anagrafic elements
        '''
        cursor=self._connect(cr, uid, context=context)

        ID_azienda = 6 # TODO change and find default company value

        # --------------------
        # Import all Company
        # --------------------
        try:
            _logger.info("Import Docnaet Company") 
            import_pool = self.pool.get("docnaet.company")
            cursor.execute('''SELECT * FROM Ditte;''') 
            for item in cursor:
                document_id = import_pool.search(cr, uid, [('docnaet_id', '=', item["ID_ditta"])])            
                if document_id: # Update
                    pass # Not updated for now!
                else: # Create
                    import_pool.create(cr, uid, {'docnaet_id': item["ID_ditta"],
                                                 'name': item["ditRagioneSociale"],
                                                 'note': item["ditNote"],
                                                }, context=context)
        except: 
            _logger.error(sys.exc_info()) # Raise error import protocols

        # --------------------
        # Import all Protocols
        # --------------------
        try:
            _logger.info("Import Docnaet Protocols") 
            import_pool = self.pool.get("docnaet.protocol")
            cursor.execute('''SELECT * FROM Protocolli WHERE ID_azienda = %s;''', (ID_azienda,)) # TODO change
            for item in cursor:
                document_id = import_pool.search(cr, uid, [('docnaet_id', '=', item["ID_protocollo"])])            
                if document_id: # Update
                    pass # Not updated for now!
                else: # Create
                    import_pool.create(cr, uid, {
                        'docnaet_id': item["ID_protocollo"],
                        'name': item["proDescrizione"],
                        'note': item["proNote"],
                        }, context=context)
        except: 
            _logger.error(sys.exc_info()) # Raise error import protocols

        # --------------------
        # Import all Language
        # --------------------
        try:
            _logger.info("Import Docnaet Language") 
            import_pool = self.pool.get("docnaet.language")
            cursor.execute('''SELECT * FROM Lingue;''')
            for item in cursor:
                document_id = import_pool.search(cr, uid, [('docnaet_id', '=', item["ID_lingua"])])            
                if document_id: # Update
                    pass # Not updated for now!
                else: # Create
                    import_pool.create(cr, uid, {'docnaet_id': item["ID_lingua"],
                                                 'name': item["linDescrizione"],
                                                 'note': item["linNote"],
                                                }, context=context)
        except: 
            _logger.error(sys.exc_info()) # Raise error import protocols

        # ---------------------
        # Import all Type
        # ---------------------
        try:
            _logger.info("Import Docnaet Type") 
            import_pool = self.pool.get("docnaet.type")
            cursor.execute('''SELECT * FROM Tipologie;''') 
            for item in cursor:
                document_id = import_pool.search(cr, uid, [('docnaet_id', '=', item["ID_tipologia"])])            
                if document_id: # Update
                    pass # Not updated for now!
                else: # Create
                    import_pool.create(cr, uid, {'docnaet_id': item["ID_tipologia"],
                                                 'name': item["tipDescrizione"],
                                                 'note': item["tipNote"],
                                                }, context=context)
        except: 
            _logger.error(sys.exc_info()) # Raise error import protocols

        # ---------------------
        # Import all User
        # ---------------------
        try:
            _logger.info("Import Docnaet User") 
            import_pool = self.pool.get("docnaet.user")
            cursor.execute('''SELECT * FROM Utenti;''')
            for item in cursor:
                document_id = import_pool.search(cr, uid, [('docnaet_id', '=', item["ID_utente"])])            
                if document_id: # Update
                    pass # Not updated for now!
                else: # Create
                    import_pool.create(cr, uid, {'docnaet_id': item["ID_utente"],
                                                 'name': item["uteDescrizione"],
                                                 #'note': item["uteNote"],
                                                }, context=context)
        except: 
            _logger.error(sys.exc_info()) # Raise error import protocols

    def import_document_deadlined(self, cr, uid, context=None):
        ''' Import a list of document having ID in Docnaet DB
        '''
        # Import anagrafic used in documents:
        res = self.sync_all_secondary_anagrafic(cr, uid, context=context)
        
        cursor = self._get_document_deadlined(cr, uid, context=context)
        if not cursor:
            return False
        
        # Pool:
        protocol_pool=self.pool.get('docnaet.protocol')
        language_pool=self.pool.get('docnaet.language')
        type_pool=self.pool.get('docnaet.type')
        company_pool=self.pool.get('docnaet.company')
        user_pool=self.pool.get('docnaet.user')
        
        deadlined_ids = []
        for item in cursor: # togliere
            data = {
                    'name': "[N. %s] %s"%(item["docNumero"], item["docOggetto"],),
                    'number': item["docNumero"],                    
                    'date': item["docData"].strftime('%Y-%m-%d') if item["docData"] else False,
                    'deadline': item["docScadenza"].strftime('%Y-%m-%d') if item["docScadenza"] else False,
                    'deadline_extra':item["docMotivo"],
                    'description': item["docDescrizione"],
                    'note': item["docNote"],
                    'user_id': user_pool.docnaet_2_openerp_id(cr, uid, item["ID_utente"], context=context) if item["ID_utente"] else False,
                    'partner_id': False, #item[""],

                    # OpenERP many2one:
                    'protocol_id': protocol_pool.docnaet_2_openerp_id(cr, uid, item["ID_protocollo"], context=context) if item["ID_protocollo"] else False,
                    'language_id': language_pool.docnaet_2_openerp_id(cr, uid, item["ID_lingua"], context=context) if item["ID_lingua"] else False, 
                    'type_id': type_pool.docnaet_2_openerp_id(cr, uid, item["ID_tipologia"], context=context) if item["ID_tipologia"] else False,
                    'company_id': company_pool.docnaet_2_openerp_id(cr, uid, item["docAzienda"], context=context) if item["docAzienda"] else False,

                    # Docnaet ID (for open document):
                    'docnaet_protocol_id': item["ID_protocollo"],
                    'docnaet_language_id': item["ID_lingua"],
                    'docnaet_type_id': item["ID_tipologia"],
                    'docnaet_company_id': item["docAzienda"],
                    'docnaet_document_id': item["ID_documento"],
                    'docnaet_document_real_id': item["docFile"],
                    'docnaet_client_id': item["ID_cliente"],
                    'docnaet_user_id': item["ID_utente"],
                    'docnaet_extension': item["docEstensione"],
                    #docScaduto
                   }
            document_id=self.search(cr, uid, [('docnaet_document_id','=',item["ID_documento"])])
            if document_id:
                self.write(cr, uid, document_id, data, context=context)
                item_id = document_id[0]
            else:    
                item_id = self.create(cr, uid, data, context=context)
            deadlined_ids.append(item_id)

        # delete deadline if not in this list and is with deadlined
        deadline_not_necessary_ids = self.search(cr, uid, [('id','not in',deadlined_ids),('deadline','!=',False)], context=context)        
        res = self.write(cr, uid, deadline_not_necessary_ids, {'deadline': False,}, context=context)
        return deadlined_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
