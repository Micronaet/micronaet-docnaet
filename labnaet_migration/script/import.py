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
import csv
import erppeek
import ConfigParser

# -----------------------------------------------------------------------------
# Read parameters:
# -----------------------------------------------------------------------------
config = ConfigParser.ConfigParser()
config.read(['config.cfg'])

server = config.get('OpenERP', 'server')
port = config.get('OpenERP', 'port')
dbname = config.get('OpenERP', 'dbname')
user = config.get('OpenERP', 'user')
password = config.get('OpenERP', 'password')

path = config.get('csv', 'path')
header = eval(config.get('csv', 'header'))
delimiter = config.get('csv', 'delimiter')

docnaet_mode = 'labnaet'

# -----------------------------------------------------------------------------
# Client ODOO:
# -----------------------------------------------------------------------------
erp = erppeek.Client(
    'http://%s:%s' % (server, port),
    db=dbname,
    user=user,
    password=password,
    )

# -----------------------------------------------------------------------------
#                             Convertion function:
# -----------------------------------------------------------------------------
def prepare_string(value):
    ''' Return formatted string
    '''
    value = value or ''
    try:
        return value.strip()
    except:
        print "Convert error: %s" % value

def prepare_bool(value):
    ''' Return formatted boolean
    '''
    return value.strip() == 1 # True

def prepare_int(value):
    ''' Return formatted int
    '''
    try: 
        return int(value.strip())
    except:
        return 0    

def prepare_float(value):
    ''' Return formatted float
    '''
    try: 
        return float(value.strip())
    except:
        return 0.0

def prepare_date(value):
    ''' Return formatted date from dd/mm/yy in yyyy/mm/dd
    '''    
    value = value.strip()    
    if len (value) < 8:
        res = False
    else:    
        res = "%s/%s/%s" % (
            "20%s" % value[6:8] if value[6:8] < '50' else "19%s" % value[6:8],
            value[0:2],
            value[3:5],
            )
    return res        

# -----------------------------------------------------------------------------
#                             Mapping importations
# -----------------------------------------------------------------------------
# Priority (not used in real docnaet)
# TODO verificare che non sia presente
priority = 'normal'

partner_type = {}
# TODO sarà vuota (non era usata per i clienti ma per prodotto)

language = {
    11: 1, # 'Italiano'
    12: 3, # 'Francese'
    13: 4, # 'Tedesco'
    17: 2, # 'Inglese'
    18: 5, # 'Spagnolo'
    }

users = {
    # TODO mapping manuale
    # TODO settare poi utente labnaet e gruppo labnaet 
    1: 1, # "Administrator" ADM
    2: 17, # "Nicola" ADM
    3: 22, # "Valeria" ADM
    4: 4, # "Vago" ADM 
    6: 1, # "Alessandro"
    7: 9, # "Simona" ADM
    9: 6, # "Mauro" 
    11: 5, # "Marcello" ADM 
    12: 16, # "Giuseppe"
    13: 13, # "Patrizia"
    14: 24, # "Elisabetta"
    15: 25, # "Laboratorio"
    16: 26, # "Amministrazione"
    17: 1, # "Wilma" RIMOSSA
    18: 29, # "Veronica"
    19: 11, # "Cassandra" ADM
    20: 32, # "Claudio"
    }

# Ditte 
company_id = 1

# Spedito << TODO import current

# -----------------------------------------------------------------------------
#                            Automatic migration:
# -----------------------------------------------------------------------------
# ------------
# Applicazioni 
# ------------
# TODO vedere se farlo calcolare in automatico (in base a estensione)
application = {}

# ----------
# Protocolli 
# ----------
filename = 'Protocolli.txt'
print 'Import %s' % filename
protocol = {}
erp_pool = erp.DocnaetProtocol
csv_file = os.path.expanduser(
    os.path.join(path, filename))

lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = - header   
tot_cols = False
for line in lines:
    try:
        i += 1
        if i <= 0:
            continue # jump intestation
        if not tot_cols: # save for test 
            tot_cols = len(line)
        
        if tot_cols != len(line):
            print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
            continue
        
        # read fields:    
        docnaet_id = int(line[0])
        name = line[1].strip()
        next = eval(line[2].strip())
        note = line[3].strip()
        #application_id = eval(line[5].strip())
        
        data = {
            'docnaet_mode': docnaet_mode,
            'name': name,
            'note': note,
            'docnaet_id': docnaet_id, # XXX ???
            #'company_id': company_id,
            'next': next,
            }

        item_ids = erp_pool.search([
            ('name', '=', name),
            ('docnaet_mode', '=', docnaet_mode),
            ])
        if item_ids:
            openerp_id = item_ids[0]
            erp_pool.write(openerp_id, data) # TODO No update
            print "%s. Update %s: %s" % (i, csv_file.split('.')[0], name)    
        else:        
            openerp_id = erp_pool.create(data).id          
            print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)    
        protocol[docnaet_id] = openerp_id # Mapping
    except:
        print "%s. Error %s: %s" % (i, csv_file.split('.')[0], name)    

# ---------
# Tipologie
# ---------
filename = 'Tipologie.txt'
print 'Import %s' % filename
tipology = {}
erp_pool = erp.DocnaetType
csv_file = os.path.expanduser(
    os.path.join(path, filename))

lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = - header   
tot_cols = False
for line in lines:
    i += 1
    if i <= 0:
        continue # jump intestation
    if not tot_cols: # save for test 
        tot_cols = len(line)
    
    if tot_cols != len(line):
        print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
        continue
    
    # read fields:    
    docnaet_id = int(line[0])
    name = line[1].strip()
    note = line[2].strip()
    
    data = {
        'docnaet_mode': docnaet_mode,
        'name': name,
        'note': note,
        'docnaet_id': docnaet_id,
        }
    item_ids = erp_pool.search([
        ('name', '=', name),
        ('docnaet_mode', '=', docnaet_mode),
        ])
    if item_ids:
        openerp_id = item_ids[0]
        #erp_pool.write(openerp_id, data) # No update
        print "%s. Yet present not updated %s: %s" % (
            i, csv_file.split('.')[0], name)    
    else:        
        openerp_id = erp_pool.create(data).id      
        print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)    
    tipology[docnaet_id] = openerp_id


# -----------------
# Nazioni > Partner
# -----------------
filename = 'Nazioni.txt' # Partner
print 'Import %s' % filename
jump = False
partner = {} # TODO partner
erp_pool = erp.ResPartner
csv_file = os.path.expanduser(os.path.join(path, filename))
lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = - header   
tot_cols = False
code_temp = 0 # TODO run direct first time!!
f_temp = open('clienti_da_associare.csv', 'w')

# Read client mapping:
import pdb; pdb.set_trace()
client_mapping = {}
for line in open('map_client.csv', 'r'): # TODO check filename if present
    line = line.strip()
    line_ids = line.split(';')
    if len(line_ids) != 2:
        continue
    client_mapping[line_ids[0]] = line_ids[1]
import pdb; pdb.set_trace()

for line in lines:
    if jump:
        break
    
    i += 1
    if i <= 0:
        continue # jump intestation
    code_temp += 1
    if not tot_cols: # save for test 
        tot_cols = len(line)
    
    if tot_cols != len(line):
        print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
        continue
    
    # read fields:    
    labnaet_id = int(line[0]) # XXX Partner used labnaet ID in this procedure
    name = line[1].strip()
    
    if name in client_mapping: # Remapped name:
        item_ids = erp_pool.search([
            ('name', 'like', client_mapping[name]),
            ])
    else:
        item_ids = erp_pool.search([
            ('name', '=ilike', name),
            ])
        
    data = {
        'docnaet_enable': True,
        #'name': name, # XXX not write (for remapped name)
        'labnaet_id': labnaet_id, # Docnaet yet done!

        #'code': code,
        #'country_id': country.get(id_nazione, False),
        #'company_id': company_id,
        }
    if item_ids:
        openerp_id = item_ids[0]
        erp_pool.write(openerp_id, data) # XXX update for enabling
        print "%s. Yet present updated %s: %s" % (
            i, csv_file.split('.')[0], name)    
    else: # not updated, use company
        openerp_id = 1 # XXX missed ID!!!
        print "%s. Not created %s: %s" % (i, csv_file.split('.')[0], name)    
        f_temp.write('{}\n'.format(name))
        
    partner[labnaet_id] = openerp_id
# TODO update with mapping manual files    
sys.exit() # TODO remove
    

# --------------------------------------
# Categorie Clienti > Categorie Prodotti
# --------------------------------------
import pdb; pdb.set_trace()
filename = 'Tipi.txt'
print 'Import %s' % filename
product_type = {}
erp_pool = erp.ProductProductDocnaet
csv_file = os.path.expanduser(
    os.path.join(path, filename))

lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = - header
tot_cols = False
for line in lines:
    i += 1
    if i <= 0:
        continue # jump intestation
    if not tot_cols: # save for test 
        tot_cols = len(line)
    
    if tot_cols != len(line):
        print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
        continue
    
    # read fields:    
    docnaet_id = int(line[0])
    name = line[1].strip()
    note = line[2].strip()
    
    data = {
        'name': name,
        'note': note,
        'docnaet_id': docnaet_id,
        }
    item_ids = erp_pool.search([
        ('name', '=', name),
        ])
    if item_ids:
        openerp_id = item_ids[0]
        erp_pool.write(openerp_id, data) # No update
        print "%s. Yet present updated %s: %s" % (
            i, csv_file.split('.')[0], name)    
    else:        
        openerp_id = erp_pool.create(data).id      
        print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)    
    product_type[docnaet_id] = openerp_id

# ------------------
# Clienti > Prodotti
# ------------------
import pdb; pdb.set_trace()
filename = 'Clienti.txt' # Real: prodotti
print 'Import %s' % filename
jump = False
product = {}
erp_pool = erp.DocnaetProduct
csv_file = os.path.expanduser(
    os.path.join(path, filename))

lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = -header   
tot_cols = False
for line in lines:
    if jump:
        break
    i += 1
    if i <= 0:
        continue # jump intestation
    if not tot_cols: # save for test 
        tot_cols = len(line)
    if i % 100 == 0:
        print 'Import %s #%s' % (filename, i)
    
    if tot_cols != len(line):
        print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
        continue
        
    # Read fields:
    docnaet_id = int(line[0])
    name = line[1].strip()
    partner_code = int(line[9].strip() or '0') # wrong: nation
    type_code = int(line[10].strip() or '0') # wrong: type of partner
    
    # Get om relation: 
    partner_id = partner.get(partner_code, False)
    type_id = product_type.get(type_code, False)
    
    item_ids = erp_pool.search([('name', '=', name)])
    data = {
        'name': name,
        'docnaet_id': docnaet_id,
        'docnaet_category_id': type_id,
        'partner_id': partner_id,
        #'company_id': company_id,
        }
    if item_ids:
        openerp_id = item_ids[0]
        erp_pool.write(openerp_id, data)
        print "%s. Update product %s: %s" % (i, csv_file.split('.')[0], name)    
    else:        
        openerp_id = erp_pool.create(data).id
        print "%s. To create %s: %s" % (i, csv_file.split('.')[0], name)        
    product[docnaet_id] = openerp_id

# ---------
# Documenti 
# ---------
import pdb; pdb.set_trace()
print 'IN PRODUZIONE CAMBIARE SETTAGGIO UTENTE!' # sui files?
filename = 'Documenti.txt'
print 'Import %s' % filename
document = {}
erp_pool = erp.DocnaetDocument
csv_file = os.path.expanduser(os.path.join(path, filename))

# TODO Attenzione ai documenti puntatori (doppio ciclo per assegnazione parent)
lines = csv.reader(open(csv_file, 'rb'), delimiter=delimiter)   
i = -header   
tot_cols = False
for line in lines:
    try:
        i += 1    
        if i <= 0:
            continue # jump intestation
        if not tot_cols: # save for test 
            tot_cols = len(line)
        
        if tot_cols != len(line):
            print "%s. Jump line: different cols %s > %s" % (tot_cols, len(line))
            continue
        
        # ---------------------------------------------------------------------
        # read fields:    
        # ---------------------------------------------------------------------
        docnaet_id = prepare_int(line[0])     
        protocol_code = prepare_int(line[1])
        language_code = prepare_int(line[2])
        type_code = prepare_int(line[3])
        support_code = prepare_int(line[4])
        partner_code = prepare_int(line[5]) # product
        name = prepare_string(line[6]) or '...'
        description = prepare_string(line[7])
        note = line[8].strip() #prepare_string(line[8])
        date = prepare_date(line[9])
        file_name = prepare_string(line[10])
        deadline = prepare_date(line[11])
        deadlined = prepare_bool(line[12])
        deadline_reason = prepare_string(line[13])
        suspended = prepare_bool(line[14])
        access = prepare_int(line[15])
        #company_code = prepare_int(line[16])
        number = prepare_int(line[17])
        fax = prepare_int(line[18])
        user_code = prepare_int(line[19])
        date_create = prepare_date(line[20])
        #control = line[21].strip()
        extension = prepare_string(line[22]).lower()
        product_code = prepare_int(line[23]) # empty
        ## NO old_id = line[24].strip()
        
        # ---------------------------------------------------------------------
        # Relations:
        # ---------------------------------------------------------------------
        # Convert code in ID:
        protocol_id = protocol.get(protocol_code, False)
        if not protocol_id:
            print "%s. Error protocol docnaet ID: %s" % (i, protocol_code)    
            continue # TODO use a "Not found" protocol

        language_id = language.get(language_code, False) # no warn if error
        type_id = tipology.get(type_code, False) # no warn if error
        user_id = 1 # TODO USE: users.get(user_code, 1) # No warning or error (set admin)
        #partner_id = partner.get(partner_code, 1)
        partner_id = False
        product_id = product.get(partner_code, False)
        
        # Create / Update operations:
        data = {        
            'docnaet_mode': docnaet_mode,
            'company_id': company_id,
            'partner_id': partner_id,
            'product_id': product_id,
            'user_id': user_id,
            'protocol_id': protocol_id,
            'language_id': language_id,
            'type_id': type_id,
            
            'name': name,
            'date': date or '1900/01/01',
            #'deadline': deadline, # not implemented in docnaet
            #'deadline_info': deadline_reason, # not implemented in docnaet
            'description': description,
            'note': note,
            'number': number,
            'fax_number': fax,
            'docnaet_extension': extension,
            'filename': file_name,
            'docnaet_id': docnaet_id,           
            'priority': priority,
            # TODO linked document!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            }
        item_ids = erp_pool.search([
            ('docnaet_mode', '=', docnaet_mode), # Labnaet document:
            ('docnaet_id', '=', docnaet_id),
            ])
        if item_ids:
            openerp_id = item_ids[0]
            erp_pool.write(openerp_id, data) # No update
            print "%s. Update %s: %s" % (i, csv_file.split('.')[0], name)    
        else:        
            #data['id'] = openerp_id # preserve ID
            openerp_id = erp_pool.create(data).id           
            # Force same ID:
            #erp_pool.write(openerp_id, {
            #    'id': docnaet_id,
            #    })    
            print "%s. Create %s: %s" % (i, csv_file.split('.')[0], name)            
        #document[docnaet_id] = openerp_id # XXX change if works!!!!!!!!!!!!!!!
    except:
        print "%s. Error document import: %s" % (i, data)
        #print sys.exc_info()

import pdb; pdb.set_trace()
print 'Remember to change labnaet_id sequence after!!!'
print 'Remember to force workflow when migrate'

# -----------------------------------------------------------------------------
#                                Not migration
# -----------------------------------------------------------------------------
# NOTE: 
# not imported (see res.partner category)
# Prodotti
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
