#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import ConfigParser
    
# -----------------------------------------------------------------------------
# Test remote or LAN mode (for choose config file):
# -----------------------------------------------------------------------------
# Remote mode end: [R]
command_line = sys.argv[1]

# Check OS:
if os.name == 'posix': # Linux mode
    linux = True
    config_file = 'openerp.cfg'
else:
    linux = False
    config_file = 'openerp.cfg' # XXX now are the same, consider use "win."

# Check remote mode call:
if command_line.endswith('[R]'):
    remote = True
    config_file = 'remote.%s' % config_file
    command_line = command_line[:-3] # Remove [R] part from command
else:
    remote = False

# -----------------------------------------------------------------------------
#                                Parameters
# -----------------------------------------------------------------------------
current_path = os.path.expanduser(os.path.dirnamae(__file__))
#current_path = os.path.expanduser(
#    os.path.dirname(
#        os.path.os.path.realpath(__file__)))

# Config file (home folder of current user):
cfg_file = os.path.join(current_path, config_file)
config = ConfigParser.ConfigParser()
config.read([cfg_file])

# Folder:
if remote:
    cfg_remote_file = os.path.join(current_path, 'remote.%s' % config_file)
    config_remote = ConfigParser.ConfigParser()
    config_remote.read([cfg_remote_file])
    store_path = config.get('folder', 'store_path')
else:
    store_path = config.get('folder', 'store_path')

private_path = config.get('folder', 'private_path') # not used in remote mode

# Command
protocol = config.get('command', 'protocol')
separator = config.get('command', 'separator')
folder_command = config.get('command', 'folder_command')
openfile_command = config.get('command', 'openfile_command')

# Log:
log_file = config.get('log', 'file')
log_f = open(log_file, 'a')

# -----------------------------------------------------------------------------
# Parse elements:
# -----------------------------------------------------------------------------
command = sys.argv[1][len(protocol):].split(separator)
if len(command) != 2:
    log_f.write('Not enought parameters\n')
    log_f.close()
    sys.exit()
operation, argument = command

# ----------------------------------------------------------------------------
# Operations: 
# ----------------------------------------------------------------------------
# -------------
# 1. Open file:
# -------------
document_pid = False
if operation == 'document':
    filename = os.path.join(store_path, argument)
    log_f.write('Open doc: %s\n' % filename)
    log_f.close()
    cmd = openfile_command % filename
    proc = subprocess.Popen(cmd.split(), shell=True) # XXX no extra space!!
    document_pid = proc.pid
    #print 'Current Document PID: %s' % document_pid
    #os.system(cmd)

# ---------------
# 2. Open folder:
# ---------------
elif not remote and operation == 'folder':
    folder = os.path.join(private_path, argument)       
    if folder[-1] == '/':
        folder = folder[:-1]
    log_f.write('Open user folder: %s\n' % folder)
    log_f.close()
    os.system('%s %s' % (folder_command, folder))    

# -----------------------------
# E: Error no correct operation
# -----------------------------
else:
    log_f.write('Error not managed operation: %s (%s)\n' % (
        operation, 'remote' if remote else 'LAN'))
    log_f.close()

# -----------------------------
# T: Try closing TAB in Firefox
# -----------------------------
try:
    # Need to be installed
    import psutil
    import win32com.client    
    from win32gui import GetWindowText, GetForegroundWindow
    #import wmi
    
    # Create scripting shell:
    shell = win32com.client.Dispatch('WScript.Shell')            
    pid_ids = [p.pid for p in psutil.process_iter() if 'firefox' in p.name()]
    if pid_ids:
        pid = pid_ids[-1] # last
        shell.AppActivate(pid)
        #print 'Kill Firefox PID: %s' % pid
        shell.SendKeys('^{F4}') # CTRL + F4
       
except:
    log_f.write('No Win 32 com library (so no close TAB)')

# --------------------------
# S: Show windows with focus
# --------------------------
if document_pid:
    shell.AppActivate(document_pid)
    
