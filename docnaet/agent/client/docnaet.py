#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from ConfigParser import ConfigParser

# -----------------------------------------------------------------------------
#                         PARSE COMMAND LAUNCH:
# -----------------------------------------------------------------------------
# Read second part of command:
command_line = sys.argv[1]  # LAN/Local or Labnaet/Docnaet
command_line = command_line.replace('%7C', '|').replace('%7c', '|')
command_line = command_line.rstrip('/')  # remove trail /

# -----------------------------------------------------------------------------
# Check OS:
# -----------------------------------------------------------------------------
if os.name == 'posix':  # Linux mode
    linux = True
    config_file = 'openerp.cfg'
else:
    linux = False
    config_file = 'openerp.cfg'  # XXX now are the same, consider use "win."

# -----------------------------------------------------------------------------
#                            Manage folder setup:
# -----------------------------------------------------------------------------
remote = False
if command_line.endswith('[R]'):
    # Check remote mode call:
    remote = True
    config_file = 'remote.%s' % config_file
    command_line = command_line[:-3]  # Remove [R] part from command
elif command_line.endswith('[L]'):
    # Check remote mode call:
    config_file = 'labnaet.cfg'
    command_line = command_line[:-3]  # Remove [R] part from command
else:  # ends with [D] or nothing >> Docnaet
    # Check remote mode call:
    # config_file = 'docnaet.cfg'
    pass  # XXX Nothing for now

# -----------------------------------------------------------------------------
#                               Parameters
# -----------------------------------------------------------------------------
# A. Static:
close_tab = False  # todo put in config file
current_path = os.path.expanduser(os.path.dirname(__file__))

# Read config file: XXX Manage error for file
cfg_file = os.path.join(current_path, config_file)
config = ConfigParser()
config.read([cfg_file])

# B. File cfg selected:

# Folder:
store_path = config.get('folder', 'store_path')
private_path = config.get('folder', 'private_path')

# Command
protocol = config.get('command', 'protocol')
separator = config.get('command', 'separator')
folder_command = config.get('command', 'folder_command')
openfile_command = config.get('command', 'openfile_command')

# Log:
log_file = config.get('log', 'file')

# Extra parameters:
log_f = open(log_file, 'a')

# -----------------------------------------------------------------------------
# Parse elements:
# -----------------------------------------------------------------------------
command = command_line[len(protocol):].split(separator)
if len(command) != 2:
    log_f.write(u'Not enough parameters: %s\n' % command_line)
    log_f.close()
    sys.exit()

# Split 2 part of command:
operation, argument = command

# =============================================================================
#                                 Operations:
# =============================================================================
# 1. Open file:
# -----------------------------------------------------------------------------
document_pid = False
if operation.lower() == 'document':

    # A. Try direct fullname:
    filename = argument
    fullname = os.path.join(store_path, filename)
    # filename = os.path.basename(fullname)

    if not os.path.isfile(fullname):
        try:
            # Extract number for generate folder:
            number = int(filename.split('.')[0])
            file_folder = str(number / 10000)

            # B. Add extra folder:
            fullname = os.path.join(store_path, file_folder, filename)
            if not os.path.isfile(fullname):
                log_f.write('Error file not present: %s\n' % fullname)
                sys.exit()  # End program
        except:
            log_f.write('Error convert ID: %s\n' % fullname)
            sys.exit()  # End program

    log_f.write('Open doc: %s\n' % fullname)
    log_f.close()
    cmd = openfile_command % fullname
    proc = subprocess.Popen(cmd.split(), shell=True)  # XXX no extra space!!
    document_pid = proc.pid

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
    log_f.write('Error operation not managed: %s (%s)\n' % (
        operation, 'remote' if remote else 'LAN'))
    log_f.close()

if close_tab:
    # -------------------------------------------------------------------------
    # T: Try closing TAB in Firefox
    # -------------------------------------------------------------------------
    try:
        # Need to be installed
        import psutil
        import win32com.client
        from win32gui import GetWindowText, GetForegroundWindow
        # import wmi

        # Create scripting shell:
        shell = win32com.client.Dispatch('WScript.Shell')
        pid_ids = [
            p.pid for p in psutil.process_iter() if 'firefox' in p.name()]
        if pid_ids:
            pid = pid_ids[-1]  # last
            shell.AppActivate(pid)
            # print 'Kill Firefox PID: %s' % pid
            shell.SendKeys('^{F4}')  # CTRL + F4
    except:
        log_f.write('No Win 32 com library (so no close TAB)')

    # -------------------------------------------------------------------------
    # S: Show windows with focus
    # -------------------------------------------------------------------------
    if document_pid:
        shell.AppActivate(document_pid)
