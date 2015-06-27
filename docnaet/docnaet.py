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
import openerp.netsvc
import logging
from openerp.osv import osv, orm, fields
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)


class docnaet_language(osv.osv):
    ''' Object docnaet.language
    '''    
    _name = 'docnaet.language'
    _description = 'Docnaet language'
    _order = 'name'

    def docnaet_2_openerp_id(self, cr, uid, docnaet_id, context=None):
        ''' Search docnaet ID and return OpenERP ID
        '''
        oerp_id = self.search(cr, uid, [('docnaet_id','=',docnaet_id)])
        if oerp_id:
            return oerp_id[0]
        else:
            return False
                
    _columns = {        
        'name': fields.char('Language', size=64, required=False, readonly=False),
        'docnaet_id': fields.integer('Docnaet ID', required=False, readonly=False),
        'note': fields.text('Note'),
    }

class docnaet_type(osv.osv):
    ''' Object docnaet.type
    '''    
    _name = 'docnaet.type'
    _description = 'Docnaet type'
    _order = 'name'

    def docnaet_2_openerp_id(self, cr, uid, docnaet_id, context=None):
        ''' Search docnaet ID and return OpenERP ID
        '''
        oerp_id = self.search(cr, uid, [('docnaet_id','=',docnaet_id)])
        if oerp_id:
            return oerp_id[0]
        else:
            return False

    _columns = {        
        'name': fields.char('Type', size=64, required=False, readonly=False),
        'docnaet_id': fields.integer('Docnaet ID', required=False, readonly=False),
        'note': fields.text('Note'),
    }

class docnaet_user(osv.osv):
    ''' Object docnaet.user
    '''    
    _name = 'docnaet.user'
    _description = 'Docnaet user'
    _order = 'name'

    def docnaet_2_openerp_id(self, cr, uid, docnaet_id, context=None):
        ''' Search docnaet ID and return OpenERP ID
        '''
        user_pool = self.pool.get("res.users")
        admin_id = user_pool.search(cr, uid, [('login','=','admin')])

        oerp_id = self.search(cr, uid, [('docnaet_id','=',docnaet_id)])
        if oerp_id:
            user_id = user_pool.search(cr, uid, [('docnaet_user_id','=',oerp_id[0])])
            if user_id:
                user_proxy = user_pool.browse(cr, uid, user_id)[0]
                #organizer = "%s <%s>"%(user_proxy.name, user_proxy.email)
                return user_id[0] #, organizer   # Togliere quando trovato errore creazione / thread
        return admin_id[0] if admin_id else False # Togliere quando trovato errore creazione / thread

    def docnaet_2_openerp_organizer(self, cr, uid, docnaet_id, context=None):
        ''' Search organizer and return OpenERP ID
        '''
        if not docnaet_id:
             return False
        
        user_pool = self.pool.get("res.users")
        user_ids = user_pool.search(cr, uid, [('docnaet_user_id','=',docnaet_id)])
        if user_ids:
            user_proxy = user_pool.browse(cr, uid, user_ids)[0]
            return  "%s <%s>"%(user_proxy.name, user_proxy.email)
        return False #admin_id[0] if admin_id else False # Togliere quando trovato errore creazione / thread

    _columns = {        
        'name': fields.char('User', size=64, required=False, readonly=False),
        'docnaet_id': fields.integer('Docnaet ID', required=False, readonly=False),
        'note': fields.text('Note'),
    }

class docnaet_company(osv.osv):
    ''' Object docnaet.company
    '''    
    _name = 'docnaet.company'
    _description = 'Docnaet company'
    _order = 'name'

    def docnaet_2_openerp_id(self, cr, uid, docnaet_id, context=None):
        ''' Search docnaet ID and return OpenERP ID
        '''
        oerp_id = self.search(cr, uid, [('docnaet_id','=',docnaet_id)])
        if oerp_id:
            return oerp_id[0]
        else:
            return False

    _columns = {        
        'name': fields.char('Company', size=64, required=False, readonly=False),
        'docnaet_id': fields.integer('Docnaet ID', required=False, readonly=False),
        'note': fields.text('Note'),
    }

class docnaet_protocol(osv.osv):
    ''' Object docnaet.protocol
    '''    
    _name = 'docnaet.protocol'
    _description = 'Docnaet protocol'
    _order = 'name'

    def docnaet_2_openerp_id(self, cr, uid, docnaet_id, context=None):
        ''' Search docnaet ID and return OpenERP ID
        '''
        oerp_id = self.search(cr, uid, [('docnaet_id','=',docnaet_id)])
        if oerp_id:
            return oerp_id[0]
        else:
            return False

    _columns = {        
        'name': fields.char('Protocol', size=64, required=False, readonly=False),
        'docnaet_id': fields.integer('Docnaet ID', required=False, readonly=False),
        'note': fields.text('Note'),
    }

class docnaet_document(osv.osv):
    ''' Object docnaet.document
    '''    
    _name = 'docnaet.document'
    _description = 'Docnaet document'
    _order = 'date,name'

    # --------------------
    # Utility and function
    # --------------------
    def docnaet_2_openerp_id(self, cr, uid, docnaet_id, context=None):
        ''' Search docnaet ID and return OpenERP ID
        '''
        oerp_id = self.search(cr, uid, [('docnaet_id','=',docnaet_id)])
        if oerp_id:
            return oerp_id[0]
        else:
            return False

    def _connect(self, cr, uid, context=None):
        ''' Connect action for link to MSSQL DB
        '''        
        try:
            connection = self.pool.get('res.company').docnaet_mssql_connect(cr, uid, context=context)  # first company
            cursor = connection.cursor()
            
            if not cursor: 
                _logger.error("Can't access Docnaet MSSQL Database!")
                return False
            return cursor
        except:
            return False    
            
    def docnaet_run_command_sql(self, cr, uid, query, context=None):
        ''' Used for run command sql query with docnaet tables via SQL connection
        '''
        import sys
        
        cursor=self._connect(cr, uid, context=context)
        try:
            cursor.execute(query)
            return True   
        except: 
            _logger.error("Query SQL error: %s!"%(sys.exc_info(),))
            return False  # Error return nothing            

    # SQL function (to get list of elements ####################################
    def _get_document_deadlined(self, cr, uid, context=None):
        ''' Get the list of document passed
        '''
        cursor=self._connect(cr, uid, context=context)
        try:
            cursor.execute('''SELECT * FROM Documenti WHERE docScadenza is not NULL;''')# WHERE ID_documento in %s;''',tuple(ids))
            return cursor # with the query setted up                  
        except: 
            return False  # Error return nothing            
    
    # TODO _get_document_deadlined()

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
        
    # -------------------------------------------------
    # Utility for URL creation:
    # -------------------------------------------------
    def button_call_url_docnaet(self, cr, uid, ids, context=None):
        ''' Call action for open form of document in docnaet
        '''
        return self.call_url(cr, uid, ids[0], context=context)

    def button_call_url_document(self, cr, uid, ids, context=None):
        ''' Call action for open form of document in docnaet
        '''
        return self.call_url(cr, uid, ids[0], docnaet_format=True, context=context)
        
    def call_url(self, cr, uid, item_id, docnaet_format=False,  context=None):
        ''' Call url if format: docnaet://
            item_id: ID of docnaet.document
            docnaet_format: True= in docnaet format require installation of 
                            docnaet.exe element + registry entry for launch
                            docnaet:// special link
                            
                            False= Get the link for open detail of document 
                            directly in Docnaet passing autentication form
        '''     
        
        docnaet_proxy = self.browse(cr, uid, item_id, context=context)

        if docnaet_format: # docnaet://
            final_url = r"docnaet://%s\%s\%s.%s"%(docnaet_proxy.docnaet_company_id, 
                                                  docnaet_proxy.docnaet_protocol_id,
                                                  docnaet_proxy.docnaet_document_real_id if docnaet_proxy.docnaet_document_real_id else docnaet_proxy.docnaet_document_id,
                                                  docnaet_proxy.docnaet_extension,     
                                                 )
        else: # Link to detail form in docnaet
            parameters = self.pool.get('res.company').get_docnaet_parameters(cr, uid, context=context)
            final_url = r"http://%s/docnaet/asp/autenticazione.asp?token=T&client_id=%s&document_id=%s&company_id=%s&user_id=%s"%(
                        parameters.docnaet_host, 
                        docnaet_proxy.docnaet_client_id, 
                        docnaet_proxy.docnaet_document_id, 
                        docnaet_proxy.docnaet_company_id, 
                        docnaet_proxy.docnaet_user_id if docnaet_proxy.docnaet_user_id else parameters.docnaet_guest_user_id.id,
                        )

        return {'type': 'ir.actions.act_url', 'url':final_url, 'target': 'new'}
                        
    _columns = {        
        'name': fields.char('Oggetto', size=64, required=False, readonly=False),
        'number': fields.char('Prot. n.', size=10, required=False, readonly=False),
        'date': fields.date('Date'),
        'deadline': fields.date('Deadline'),
        'deadline_extra': fields.char('Deadline info', size=64, required=False, readonly=False),
        'description': fields.text('Description'),
        'note': fields.text('Note'),

        # OpenERP ID-many2one 
        'protocol_id': fields.many2one('docnaet.protocol', 'Protocol', required=False),
        'language_id': fields.many2one('docnaet.language', 'Language', required=False),
        'type_id': fields.many2one('docnaet.type', 'Type', required=False),
        'company_id': fields.many2one('docnaet.company', 'Company', required=False),

        'user_id': fields.many2one('res.users', 'User', required=False),
        'partner_id': fields.many2one('res.partner', 'Partner', required=False),

        # Docnaet ID (for open document)
        'docnaet_document_id': fields.integer('Docnaet Document ID'),
        'docnaet_document_real_id': fields.integer('Docnaet Document Real ID'),
        'docnaet_protocol_id': fields.integer('Docnaet Protocol ID'),
        'docnaet_language_id': fields.integer('Docnaet Language ID'),
        'docnaet_type_id': fields.integer('Docnaet Type ID'),
        'docnaet_company_id': fields.integer('Docnaet Company ID'),  

        'docnaet_client_id': fields.integer('Docnaet Client ID'),
        'docnaet_user_id': fields.integer('Docnaet User ID'),

        'docnaet_extension': fields.char('Docnaet files ext.', size = 5, required=False, readonly=False),       
    }
    
class res_company(osv.osv):
    ''' Extra fields for res.company object 
        Used for manage parameter for Docnaet access
    '''
    _name="res.company"
    _inherit="res.company"

    def get_docnaet_parameters(self, cr, uid, company_id = 0, context=None):
        ''' Return a browse object of the default company (if not passed)
            This object will be used for get parameter for set up environment
        '''
        try: # Every error return no cursor
            if not company_id:
                company_id = self.search(cr, uid, [], context=context)[0]

            return self.browse(cr, uid, company_id, context=context)
        except:
            return False

    def docnaet_mssql_connect(self, cr, uid, company_id = 0, as_dict=True, context=None):
        ''' Connect to the ids (only one) passed and return the connection for manage DB
            ids=select company_id, if not present take the first company
        '''
        import pymssql, sys #MySQLdb, MySQLdb.cursors, sys
        try: # Every error return no cursor
            if not company_id:
                company_id = self.search(cr, uid, [], context=context)[0]

            company_proxy=self.browse(cr, uid, company_id, context=context)
            
            if company_proxy.docnaet_mssql_type=='mssql':
                conn = pymssql.connect(host = r"%s:%s"%(company_proxy.docnaet_mssql_host, company_proxy.docnaet_mssql_port), 
                                       user = company_proxy.docnaet_mssql_username, 
                                       password = company_proxy.docnaet_mssql_password, 
                                       database = company_proxy.docnaet_mssql_database,
                                       as_dict=as_dict)
                #elif company_proxy.mssql_type=='mysql':
                #    conn=MySQLdb.connect(host = company_proxy.mssql_host,
                #                       user = company_proxy.mssql_username,
                #                       passwd = company_proxy.mssql_password,
                #                       db = company_proxy.mssql_database,
                #                       cursorclass=MySQLdb.cursors.DictCursor,
                #                       charset='utf8',
                #                       )
            else:
                return False

            return conn #.cursor()
        except:
            return False

    _columns = {
        'docnaet_company_id': fields.many2one('docnaet.company', 'Docnaet Company', required=False, help="Docnaet company linked to OpenERP user (used for document operation)"),

        'docnaet_host': fields.char('Docnaet webserver name', size=64, required=False, readonly=False, help="Webserver name, Host name or IP address ex.: 10.0.0.2 or hostname: server.example.com"),
        'docnaet_mssql_host': fields.char('MS SQL server host', size=64, required=False, readonly=False, help="Host name, IP address: 10.0.0.2 or hostname: server.example.com"),
        'docnaet_mssql_port': fields.integer('MS SQL server port', required=False, readonly=False, help="Host name, example: 1433 (form MSSQL), 3306 (for MySQL)"),
        'docnaet_mssql_username': fields.char('MS SQL server username', size=64, required=False, readonly=False, help="User name, example: sa or root"),
        'docnaet_mssql_password': fields.char('MS SQL server password', size=64, required=False, readonly=False, password=True),
        'docnaet_mssql_database': fields.char('MS SQL server database name', size=64, required=False, readonly=False),
        'docnaet_guest_user_id': fields.many2one('docnaet.user', 'Docnaet guest', required=False, help="Docnaet guest user if document user in not present"),
        'docnaet_mssql_type': fields.selection(
            [
            #('mysql','Docnaet via MySQL'),
            ('mssql','Docnaet via MS SQL Server'),            
            ],'Type', select=True,),
    }
    _defaults = {
        'docnaet_mssql_port': lambda *a: 1433,
        'docnaet_mssql_type': lambda *a: 'mssql',
    }

class res_users(osv.osv):
    ''' Extra fields for res.user object 
    '''
    _name="res.users"
    _inherit="res.users"

    _columns = {
        'docnaet_user_id': fields.many2one('docnaet.user', 'Docnaet User', required=False, help="Docnaet user linked to OpenERP user (used for document operation)"),
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
