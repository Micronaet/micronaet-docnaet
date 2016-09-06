#!/usr/bin/python
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
#
# This program run under windows for agent
# maybe correct docnaet_path parametrize the creation also for linux systems
#
###############################################################################


import os
import sys
import ConfigParser
from datetime import datetime, timedelta

try:
    from Tkinter import *
    import tkMessageBox
    
    window = Tk()
    window.wm_withdraw()
    window.geometry('1x1+%s+%s' % (
        window.winfo_screenwidth() / 2,
        window.winfo_screenheight() / 2,
        ))
        
    X_interface = True
except:
    X_interface = False
    
# -----------------------------------------------------------------------------
# Fixed parameters:
# -----------------------------------------------------------------------------
# NOTE: Program run only
docnaet_path = 'C:\\Docnaet'
docnaet_config_file = 'openerp.cfg'
docnaet_config = os.path.join(docnaet_path, docnaet_config_file)

# -----------------------------------------------------------------------------
# Read config:
# -----------------------------------------------------------------------------
# Test if config file exist:
if not os.path.isfile(docnaet_config):
    # --------------
    # Create folder:
    # --------------
    try:
        os.makedirs(os.path.dirname(docnaet_path))
    except:
        pass    

    # --------------------
    # Create default file:
    # --------------------
    try:
        cfg_file = open(docnaet_config, 'w')
    except:
        if X_interface:
            tkMessageBox.showerror(
                title='Error:', 
                message='Cannot create config file [%s]' % docnaet_config, 
                parent=window)
        sys.exit()
        
    cfg_file.write('''[log]
file: c:\\Docnaet\\docnaet.log

[docnaet]
path: \\\\Muletto\\Docnaet\\Filestore
''')
    cfg_file.close()
    
    # ------------------
    # Message to config:    
    # ------------------
    if X_interface:
        tkMessageBox.showerror(
            title='Error:', 
            message='No config file, new create [%s]' % docnaet_config, 
            parent=window)
    sys.exit()    

# -----------------------------------------------------------------------------
# Read parameters from file:
# -----------------------------------------------------------------------------
config = ConfigParser.ConfigParser()
config.read([docnaet_config])

docnaet_log = config.get('log', 'file')
docnaet_path = config.get('docnaet', 'path')

f_log = open(docnaet_log, 'a')
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

if len(sys.argv) != 2:
    f_log.write('%s [ERROR] Not all parameters: %s\n' % (date, sys.argv))
    sys.exit()

# -----------------------------------------------------------------------------
# Extract operation from arguments:
# -----------------------------------------------------------------------------
# NOTE: Link format  >>>   docnaet://[operation]parameters
argument = sys.argv[1].split('//')[-1].split(']')
operation = argument[0][1:] # remove [
parameter = argument[1][:-1] # remove /

# -----------------------------------------------------------------------------
# Web Services:
# -----------------------------------------------------------------------------
if operation == 'open':
    # Extract parameters:
    parameters = parameter.split('-')
    protocol_id = parameters[0]
    document_id = parameters[1]
    
    # real: document = os.path.join(docnaet_path, document_id)
    # temp:
    document = os.path.join(docnaet_path, protocol_id, document_id) 
    command = 'start %s' % document
    f_log.write('%s [INFO] %s: %s\n' % (date, operation, command))
    
    try:
        # TODO Check file presence
        os.system(command)
    except:
        f_log.write('%s [ERROR] Wrong command %s\n' % (date, sys.exc_info()))
    
elif operation == 'home':
    pass # TODO
