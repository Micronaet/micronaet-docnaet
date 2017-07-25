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
#import os
#import sys
import wmi
import win32com.client    

c = wmi.WMI()
firefox_id = False
for process in c.Win32_Process():
    if process.Name.lower() == 'firefox.exe':
        firefox_id = process.ProcessId
        print process.ProcessId, process.Name

if firefox_id:
    shell = win32com.client.Dispatch('WScript.Shell')
    #shell.Run('firefox')
    shell.AppActivate('firefox')
    shell.AppActivate(firefox_id)
    shell.SendKeys('^{F4}') # CTRL + F4
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
