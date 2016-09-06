#!/usr/bin/python
import os
import sys
from datetime import datetime, timedelta
#import subprocess



# Parameters:
# TODO parametrize:
#docnaet_path = 'C:\\Docnaet\\FileStore'
docnaet_path = '\\MULETTO\\Docnaet\\FileStore'
docnaet_log = 'C:\\Docnaet\\Log\\docnaet.log'
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
        os.system(command)
    except:
        f_log.write('%s [ERROR] Wrong command %s\n' % (date, sys.exc_info()))
    
elif operation == 'home':
    pass # TODO
