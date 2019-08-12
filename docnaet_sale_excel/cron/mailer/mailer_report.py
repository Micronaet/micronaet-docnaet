# -*- coding: utf-8 -*-
###############################################################################
#
# ODOO (ex OpenERP) 
# Open Source Management Solution
# Copyright (C) 2001-2015 Micronaet S.r.l. (<http://www.micronaet.it>)
# Developer: Nicola Riolini @thebrush (<https://it.linkedin.com/in/thebrush>)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import erppeek
import ConfigParser
import smtplib  
from datetime import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email import Encoders

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
#cfg_file = os.path.expanduser('../local.cfg')
cfg_file = os.path.expanduser('../openerp.cfg')
now = ('%s' %datetime.now())[:19]

config = ConfigParser.ConfigParser()
config.read([cfg_file])

# ERP Connection:
odoo = {
    'database': config.get('dbaccess', 'dbname'),
    'user': config.get('dbaccess', 'user'),
    'password': config.get('dbaccess', 'pwd'),
    'server': config.get('dbaccess', 'server'),
    'port': config.get('dbaccess', 'port'),
    }

# Mail:
smtp = {
    'to': config.get('smtp', 'to'),
    #'subject': config.get('smtp', 'subject'),
    #'text': config.get('smtp', 'text'),
    'text': '''
        <p>Spett.li responsabili vendite,</p>
        <p>Questa &egrave; una mail automatica giornaliera inviata da 
            <b>OpenERP</b> con lo stato ordini in contabilit&agrave; e 
            le offerte aperte o perse in <b>Docnaet</b>.
        </p>

        <p>Situazione aggiornata alla data di riferimento: <b>%s</b></p>

        <p>
        1. <b>Ordini</b>: Elenco ordini da consegnare, fonte Mexal
           (aggiunte informazioni solvibili&agrave;).
           Ordinamento per data decrescente.<br/>
        2. <b>Offerte</b>: Documenti Docnaet valorizzati dagli agenti ancora 
           da vincere o perdere<br/>
        3. <b>Perse</b>: Offerte marcate come perse in Docnaet.<br/>
        4. <b>Clienti</b>: Elenco ordini, offerte attive, offerte perse 
           e dettaglio solvibilit&agrave; cliente. Ordinamento alfabetico.<br/>
        5. <b>Prodotti</b>: Elenco ordini per prodotto suddivisi per mese di 
           scadenza / consegna (colonna No = senza scadenza). Totalizzato in 
           fondo per unit&agrave di misura (in azzurro il mese attuale).<br/>
        </p>

        <p>
            <i>Nota: In rosso le righe dei clienti con pagamenti scaduti.</i>
        </p>
        <p>
            <i>Nota: Potrebbe capitare che ci siano differenti valute, il 
               totale indicato in fondo verr&agrave; quindi spezzato in tutte
               quelle rilevate.</i>
        </p>
        
        <b>Micronaet S.r.l.</b>
        ''' % now,
    'subject': 'Dettaglio offerte e ordini aperti: %s' % now,    
    
    'folder': config.get('smtp', 'folder'),
    }
#group_name = 'docnaet_sale_excel.group_sale_statistic_mail'

filename = os.path.expanduser(
    os.path.join(smtp['folder'], 'stato_ordini.xlsx'))
context = {
    'save_mode': filename,
    }

# -----------------------------------------------------------------------------
# Connect to ODOO:
# -----------------------------------------------------------------------------
odoo = erppeek.Client(
    'http://%s:%s' % (odoo['server'], odoo['port']), 
    db=odoo['database'],
    user=odoo['user'],
    password=odoo['password'],
    )
mailer = odoo.model('ir.mail_server')
group = odoo.model('res.groups')
model = odoo.model('ir.model.data')

# Setup context for order:
odoo.context = context
order = odoo.model('sale.order')

# Launch extract procedure:
order.extract_sale_excel_report()

# -----------------------------------------------------------------------------
# Extract mail list from group:
# -----------------------------------------------------------------------------
#group_name = group_name.split('.')
#group_id = model.get_object_reference(
#    group_name[0], 
#    group_name[1],
#    )[1]
#partner_name = []
#for user in group_pool.browse(group_id).users:
#    partner_ids.append(user.partner_id.email)

# -----------------------------------------------------------------------------
# SMTP Sent:
# -----------------------------------------------------------------------------
# Get mailserver option:
mailer_ids = mailer.search([])
if not mailer_ids:
    print '[ERR] No mail server configured in ODOO'
    sys.exit()

odoo_mailer = mailer.browse(mailer_ids)[0]

# Open connection:
print '[INFO] Sending using "%s" connection [%s:%s]' % (
    odoo_mailer.name,
    odoo_mailer.smtp_host,
    odoo_mailer.smtp_port,
    )

if odoo_mailer.smtp_encryption in ('ssl', 'starttls'):
    smtp_server = smtplib.SMTP_SSL(
        odoo_mailer.smtp_host, odoo_mailer.smtp_port)
else:
    print '[ERR] Connect only SMTP SSL server!'
    sys.exit()
    #server_smtp.start() # TODO Check

smtp_server.login(odoo_mailer.smtp_user, odoo_mailer.smtp_pass)
for to in smtp['to'].replace(' ', '').split(','):
    print 'Senting mail to: %s ...' % to
    msg = MIMEMultipart()
    msg['Subject'] = smtp['subject']
    msg['From'] = odoo_mailer.smtp_user
    msg['To'] = smtp['to'] #', '.join(self.EMAIL_TO)
    msg.attach(MIMEText(smtp['text'], 'html'))


    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(filename, 'rb').read())
    Encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition', 'attachment; filename="Stato vendite.xlsx"')

    msg.attach(part)

    # Send mail:
    smtp_server.sendmail(odoo_mailer.smtp_user, to, msg.as_string())

smtp_server.quit()
