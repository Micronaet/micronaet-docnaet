#!/usr/bin/python
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
# Parameters:
# -----------------------------------------------------------------------------
import pdb; pdb.set_trace()
docnaet_path = 'C:\\Docnaet'
docnaet_config_file = 'openerp.cfg'
docnaet_config = os.path.join(docnaet_path, docnaet_config_file)

# -----------------------------------------------------------------------------
# Read config:
# -----------------------------------------------------------------------------
# Test if config file exist:
if not os.path.isfile(docnaet_config):
    # Create folder:
    try:
        os.makedirs(os.path.dirname(docnaet_path))
    except:
        pass    
    
    # Create default file:
    cfg_file = open(docnaet_config, 'w')
    cfg_file.write('''
[log]
file: c:\\Docnaet\\docnaet.log

[docnaet]
path: \\\\Muletto\\Docnaet\\Filestore
''')
    
    # Message to config:    
    if X_interface:
        tkMessageBox.showerror(
            title='Error:', 
            message='No config file, new create [%s]' % docnaet_config, 
            parent=window)
    sys.exit()    

# Read parameters:
config = ConfigParser.ConfigParser()
config.read([docnaet_config])

# File parameter:
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
# Format: docnaet://[operation]parameters
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
