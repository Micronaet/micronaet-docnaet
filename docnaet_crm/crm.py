# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP module
#    Copyright (C) 2013 Micronaet srl (<http://www.micronaet.it>) 
#    
#    Italian OpenERP Community (<http://www.openerp-italia.com>)
#
#############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _
import sys

# enable log object for comunicate errors:
import logging
_logger = logging.getLogger(__name__)

class docnaet_document(osv.osv):
    ''' Extra fields for link docnaet (scheduled action)
    '''
    _name="docnaet.document"
    _inherit="docnaet.document"
    
    # ----------------
    # Scheduled Action
    # ----------------
    def schedule_import_docnaet_deadlined(self, cr, uid, context=None):
        ''' Action called by the schedule for import deadlined documents
            I there's some document deadlined today mail are sended to users
        '''
        # --------------------
        # Docnaet Documents 
        # --------------------
        # Import all document deadlined in Docnaet:
        _logger.info("Scheduled function: import_document_deadlined > Start import deadlined document!")

        # Load all document with deadline setted up
        doc_deadlined = self.import_document_deadlined(cr, uid, context=context)
        if doc_deadlined:
             _logger.info("Scheduled function: import_document_deadlined > Document deadlined imported!")
        else:
             _logger.error("Scheduled function: import_document_deadlined > Can't import deadlined document from Docnaet!")
        
        # --------------------
        # CMR Meeting Calendar
        # --------------------
        
        # Test the crm.meeting event for sending comunication of deadlined item
        calendar_pool = self.pool.get('crm.meeting')
        
        # List meeting not deadlined (non present in the docnaet_list):
        update_meeting_ids = calendar_pool.search(cr, uid, [('docnaet_document_id','not in', doc_deadlined),('docnaet_alert','=',True)], context=context) 
        calendar_pool.write(cr, uid, update_meeting_ids, {'docnaet_alert':False,}, context=context) #remove flag docnaet alarm
        
        # Update calendar deadline for new elements
        update_meeting_ids = calendar_pool.search(cr, uid, [('docnaet_document_id','in', doc_deadlined),], context=context) 
        to_create = doc_deadlined[:]

        for event in calendar_pool.browse(cr, uid, update_meeting_ids, context=context):
            # Update only description and deadline (if yet present)
            data = {'name': event.docnaet_document_id.name,
                    'description': "Oggetto:\n%s\nDescrizione:\n%s\nNote:\n%s"%(event.docnaet_document_id.name,
                                                                                event.docnaet_document_id.description,
                                                                                event.docnaet_document_id.note,),
                    }
            if event.docnaet_document_id.deadline: # deadline present
                data['date'] = "%s 07:00:00"%(event.docnaet_document_id.deadline,)
                data['date_deadline'] = "%s 07:15:00"%(event.docnaet_document_id.deadline,)
                data['docnaet_alert'] = True
            else:
                data['docnaet_alert'] = False
            calendar_pool.write(cr, uid, event.id, data, context=context)
            
            try:
                to_create.remove(event.docnaet_document_id.id)
            except:
                pass  # remove error during operations
                 
        # Create calendar event if not present
        for document in self.browse(cr, uid, to_create, context=context):
            data= {'name': document.name,
                   'description': "Oggetto:\n%s\nDescrizione:\n%s\nNote:\n%s"%(document.name,
                                                                               document.description,
                                                                               document.note,),
                   'docnaet_document_id': document.id,
                   'docnaet_alert': True, 
                   #partner_ids
                   'user_id': document.user_id.id or 1,
                   'date': "%s 07:00:00"%(document.deadline),
                   'date_deadline': "%s 07:15:00"%(document.deadline),
                   'duration': 0.25,
                   'class': 'public', 
                   }
            if document.user_id:
                data['organizer'] = "%s <%s>"%(document.user_id.name, document.user_id.email)
            calendar_pool.create(cr, uid, data, context=context)
        
        # -------------------------------
        # Mail template for notifications
        # -------------------------------
        alert_ids = calendar_pool.search(cr, uid, [('docnaet_alert','=', True),], context=context) # TODO deadline test ('date','<=',today)!!!!!!!!
        
        # Mail the events that are deadlined today        
        link_for_user = {}
        for event in calendar_pool.browse(cr, uid, alert_ids, context=context):
            try:
                if event.user_id.id not in link_for_user: link_for_user[event.user_id.id] = ""
                
                if event.docnaet_document_id: 
                    document_id = event.docnaet_document_id.id
                    link = self.call_url(cr, uid, document_id, docnaet_format=False, context=context)['url']
                    link1 = "<a href='%s'>Docnaet</a>" %(link)
                    link = self.call_url(cr, uid, document_id, docnaet_format=True, context=context)['url']
                    link2 = "<a href='%s'>Document</a>"%(link)
                else:
                    link1 = ""
                    link2 = ""
            except:
                link1 = ""
                link2 = ""
                        
            link_for_user[event.user_id.id] += "<strong>Prot. %s</strong>: %s [%s - %s] <br/>\n"%(event.docnaet_document_id.protocol_id.name if (event.docnaet_document_id and event.docnaet_document_id.protocol_id) else "Nessun protocollo",
                                                                                                  event.name,
                                                                                                  link1, 
                                                                                                  link2,
                                                                                                 )

        # Pool for send mail:
        mail_pool = self.pool.get('mail.mail')                        # Mail server     
        message_pool = self.pool.get('mail.message')                  # Message obj
        template_pool = self.pool.get('email.template')               # Template obj
        compose_message_pool = self.pool.get('mail.compose.message')  # Message (for render template)
                
        template_ids = template_pool.search(cr, uid, [('name','=','Alert CRM meeting'),('model','=','res.users')], context=context) 
        if not template_ids:
            _logger.error("Template not found, mail not sended!")
                                    
        template_proxy = template_pool.browse(cr, uid, template_ids, context=context)[0]
        mail_ids=[]
        for user in link_for_user.keys(): # loop on all users ID
            email_subject = compose_message_pool.render_template(cr, uid, _(template_proxy.subject), 'res.users', user)
            body_html = compose_message_pool.render_template(cr, uid, _(template_proxy.body_html), 'res.users', user)
            body_html = body_html.replace("<!--micronaet-->", link_for_user[user])
            email_to = compose_message_pool.render_template(cr, uid, _(template_proxy.email_to), 'res.users', user)
            reply_to = compose_message_pool.render_template(cr, uid, _(template_proxy.reply_to), 'res.users', user)
            email_from = compose_message_pool.render_template(cr, uid, _(template_proxy.email_from), 'res.users', user)
            
            # Create relative message for Wall
            message_id = message_pool.create(cr, uid, {
                                                       'type': 'email',
                                                       'subject': email_subject,
                                                      }) 
                                                         
            # Create mail 
            mail_ids.append(mail_pool.create(cr, uid, {
                                                       'mail_message_id': message_id,
                                                       'mail_server_id': template_proxy.mail_server_id and template_proxy.mail_server_id.id or False, 
                                                       'state': 'outgoing',
                                                       'auto_delete': template_proxy.auto_delete,
                                                       'email_from': email_from,
                                                       'email_to': email_to,
                                                       'reply_to': reply_to,
                                                       'body_html': body_html,                                                 
                                                      }, context=context))                    
        if mail_ids:
            mail_pool.send(cr, uid, mail_ids)
            _logger.info("Send %s mail for this schedulation!"%(len(mail_ids)))
        else:
            _logger.info("None mail to send in this schedulation!")
                 
        _logger.info("Scheduled function: End import deadlined and alert mail operation!")
        return True

class crm_calendar(osv.osv):
    ''' Extra fields for link docnaet elements in crm.meeting
    '''
    _name="crm.meeting"
    _inherit="crm.meeting"
    
    # Button events:
    def button_remove_docnaet_alert(self, cr, uid, ids, context=None):
        ''' Remove alert check in crm.meeting
            Remove deadline in docnaet document (via SQL)
        ''' 
        event = self.browse(cr, uid, ids, context=context)[0]
        if event.docnaet_document_id:
            query = "UPDATE Documenti SET docScadenza = '' WHERE ID_documento = %s"%(event.docnaet_document_id.docnaet_document_id,)
            print "QUERY: %s" %(query)
            if not self.pool.get('docnaet.document').docnaet_run_command_sql(cr, uid, query, context=context):
                raise osv.except_osv(_('Warning!'),
                                     _('Error updating Docnaet document deadline!\nQuery: %s'%(query,))
                                    )

        self.write(cr, uid, ids, {'docnaet_alert': False}, context=context)
        return True
        
    def button_call_url_document(self, cr, uid, ids, context=None):
        ''' Call action for open form of document in docnaet
        '''
        meeting_proxy = self.browse(cr, uid, ids, context=context)[0]
        if meeting_proxy.docnaet_document_id:
            return self.pool.get('docnaet.document').call_url(cr, uid, meeting_proxy.docnaet_document_id.id, context=context)
        else:         
            return True # raise error

    def button_call_url_docnaet(self, cr, uid, ids, context=None):
        ''' Call action for open form of document in docnaet
        '''
        meeting_proxy = self.browse(cr, uid, ids, context=context)[0]
        if meeting_proxy.docnaet_document_id:
            return self.pool.get('docnaet.document').call_url(cr, uid, meeting_proxy.docnaet_document_id.id, docnaet_format=True, context=context)
        else:
            return True # raise error

    _columns = {
        'docnaet_document_id': fields.many2one('docnaet.document', 'Docnaet document', required=False, readonly=False, help="Document linked to calendar, for deadline events"),
        #'docnaet_deadline': fields.related('docnaet_document_id', 'deadline', store=True, help="Docnaet document deadlined (used for reset date of calendar event)"),        
        'docnaet_alert': fields.boolean('Docnaet alert', help='This meeting is geneated from Docnaet and require an alert',),
    }    
    _defaults = {
        'docnaet_alert': lambda *x: False,
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
