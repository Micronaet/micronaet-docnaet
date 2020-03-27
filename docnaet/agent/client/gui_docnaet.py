#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from ConfigParser import ConfigParser
from Tkinter import *

# -----------------------------------------------------------------------------
# Utility:
# -----------------------------------------------------------------------------
def raise_message(message, title='Docnaet Message'):
    ''' Open window message
    '''
    
    # -------------------------------------------------------------------------
    # Window:
    # -------------------------------------------------------------------------
    window = Tk()
    window.title(title)
    window.geometry('300x100')
    
    # -------------------------------------------------------------------------
    # Label:
    # -------------------------------------------------------------------------
    lbl2 = Label(window, text='')
    lbl2.grid(column=0, row=0)

    lbl1 = Label(window, text=message)
    lbl1.grid(column=0, row=1)

    lbl2 = Label(window, text='')
    lbl2.grid(column=0, row=2)
    
    # -------------------------------------------------------------------------
    # Button:
    # -------------------------------------------------------------------------
    def onclick():
        sys.exit()
        
    window.bind('<Return>', onclick)

    btn1 = Button(window, text='OK', command=onclick)
    btn1.grid(column=0, row=3)
    btn1.focus_set()
    
    window.mainloop()
    

# -----------------------------------------------------------------------------
#                         PARSE COMMAND LAUNCH:
# -----------------------------------------------------------------------------
# Read second part of command:
if len(sys.argv) == 1:
    raise_message(
        message='Parameter not present in link open!',
        title='Parameter error:',
        )

command_line = sys.argv[1] # LAN/Local or Labnaet/Docnaet
command_line = command_line.rstrip('/') # remove trail /

# -----------------------------------------------------------------------------
# Check OS:
# -----------------------------------------------------------------------------
if os.name == 'posix': # Linux mode
    linux = True
    config_file = 'openerp.cfg'
else:
    linux = False
    config_file = 'openerp.cfg' # XXX now are the same, consider use "win."

# -----------------------------------------------------------------------------
# Manage folder setup:
# -----------------------------------------------------------------------------
remote = False
if command_line.endswith('[R]'):

    # Check remote mode call:
    remote = True
    config_file = 'remote.%s' % config_file
    command_line = command_line[:-3] # Remove [R] part from command
elif command_line.endswith('[L]'):

    # Check remote mode call:
    config_file = 'labnaet.cfg'
    command_line = command_line[:-3] # Remove [R] part from command
else: # ends with [D] or nothing >> Docnaet 

    # Check remote mode call:
    #config_file = 'docnaet.cfg'
    pass # XXX Nothing for now

# -----------------------------------------------------------------------------
#                                Parameters
# -----------------------------------------------------------------------------
# A. Static:
# close_tab = False # TODO put in config file
current_path = os.path.expanduser(os.path.dirname(__file__))

# Read config file: XXX Manage error for file
cfg_file = os.path.join(current_path, config_file)

if not os.path.isfile(cfg_file):
    raise_message(
        message='File %s not found!' % cfg_file, 
        title='Config file error:',
        )
config = ConfigParser()
config.read([cfg_file])

# B. File cfg selected:

# Folder:
store_path = config.get('folder', 'store_path')
private_path = config.get('folder', 'private_path')
check_file = config.get('folder', 'check_file')

# Command
protocol = config.get('command', 'protocol')
separator = config.get('command', 'separator')
folder_command = config.get('command', 'folder_command')
openfile_command = config.get('command', 'openfile_command')

# Log:
log_file = config.get('log', 'file')

# Extra parameters:
log_f = open(log_file, 'a')

if not os.path.isfile(check_file):
    raise_message(
        message='Docnaet folder not mount, call tech support!',
        title='Docnaet error:',
        )

# -----------------------------------------------------------------------------
# Parse elements:
# -----------------------------------------------------------------------------

command = command_line[len(protocol):].split(separator)
if len(command) != 2:
    raise_message(
        message='Parameter not correct: [%s]' % command_line, 
        title='Parameter error:',
        )

# Split 2 part of command:    
operation, argument = command

# -----------------------------------------------------------------------------
#                                 Operations: 
# -----------------------------------------------------------------------------
# -------------
# 1. Open file:
# -------------
document_pid = False
if operation.lower() == 'document':
    filename = os.path.join(store_path, argument)

    if not os.path.isfile(filename):
        raise_message(
            message='File not found! [%s]' % filename, 
            title='File error:',
            )

    log_f.write('Open doc: %s\n' % filename)
    log_f.close()
    cmd = openfile_command % filename
    proc = subprocess.Popen(cmd.split(), shell=True) # XXX no extra space!!
    document_pid = proc.pid

# ---------------
# 2. Open folder:
# ---------------
elif not remote and operation == 'folder':
    folder = os.path.join(private_path, argument)       
    if folder[-1] == '/':
        folder = folder[:-1]

    if not os.path.isdir(folder):
        raise_message(
            message='Folder not found! [%s]' % folder, 
            title='Folder error:',
            )

    os.system('%s %s' % (folder_command, folder))    

# -----------------------------
# E: Error no correct operation
# -----------------------------
else:
    raise_message(
        message='Error operation not managed: %s (Mode: %s)\n' % (
            operation, 'remote' if remote else 'LAN'), 
        title='File error:',
        )

"""
No more used, correct launching in Docnaet
if close_tab:
    # -------------------------------------------------------------------------
    # T: Try closing TAB in Firefox
    # -------------------------------------------------------------------------
    try:
        # Need to be installed
        import psutil
        import win32com.client    
        from win32gui import GetWindowText, GetForegroundWindow
        #import wmi
        
        # Create scripting shell:
        shell = win32com.client.Dispatch('WScript.Shell')            
        pid_ids = [
            p.pid for p in psutil.process_iter() if 'firefox' in p.name()]
        if pid_ids:
            pid = pid_ids[-1] # last
            shell.AppActivate(pid)
            #print 'Kill Firefox PID: %s' % pid
            shell.SendKeys('^{F4}') # CTRL + F4
       
    except:
        log_f.write('No Win 32 com library (so no close TAB)')

    # -------------------------------------------------------------------------
    # S: Show windows with focus
    # -------------------------------------------------------------------------
    if document_pid:
        shell.AppActivate(document_pid)
"""        
