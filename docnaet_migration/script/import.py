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

# Read parameters:
hostname = 
port
db
user
password

path
separator

# Client erpeek:
erp = erppeek.Client(
    'http://%s:%s' % (openerp.hostname, openerp.port),
    db=openerp.name,
    user=openerp.username,
    password=openerp.password,
    )

# -----------------------------------------------------------------------------
#                             Manual importations
# -----------------------------------------------------------------------------
# Importanza 
priority = {
    0: 'highest',
    1: 'high',
    2:'normal',
    3:'low',
    4: 'lowest',
    }

# Ditte 
company = {
    1: 1, # access, openerp        
    }    

# Spedito << TODO import current

# -----------------------------------------------------------------------------
#                             Automatic migration
# -----------------------------------------------------------------------------
# Utenti
filename = 'Utenti.txt'
erp_pool = erp.ResUsers
user = {}

for line in csv(
        open(os.path.expanduser(os.path.join(path, filename))), separator):
    # read fields:    
    access_id = line[0]
    name = line[1]
    
    item_ids = erp_pool.search([('name', '=', name)])
    if item_ids:
        erp_pool.write(item_ids, {})
        openerp_id = item_ids[0]
    else:
        openerp_id = erp_pool.create(item_ids, {})
    user[access_id] = openerp_id


    
# Applicazioni 
application = {}    

# Lingue 
language = {}

# Protocolli 
csv_file = 'Protocolli.txt'

# Clienti
csv_file = 'Clienti.txt'

# Nazioni
csv_file = 'Nazioni.txt'

# Tipologie
csv_file = 'Tipologie.txt'

# Documenti 
csv_file = 'Documenti.txt'

# -----------------------------------------------------------------------------
#                                Not migration
# -----------------------------------------------------------------------------
# NOTE: not imported (see res.partner category)
# Categorie 
# Tipi 
# Supporti 
# Prodotti

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
