#!/bin/bash
gconftool-2 -t string -s /desktop/gnome/url-handlers/docnaet/command 'docnaet "%s"'
gconftool-2 -s /desktop/gnome/url-handlers/docnaet/needs_terminal false -t bool
gconftool-2 -s /desktop/gnome/url-handlers/docnaet/enabled true -t bool
