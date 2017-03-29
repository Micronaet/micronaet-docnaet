#!/bin/bash
gconftool-2 -t string -s /desktop/gnome/url-handlers/oerp/command '/usr/local/bin/docnaet "%s"'
gconftool-2 -s /desktop/gnome/url-handlers/oerp/needs_terminal false -t bool
gconftool-2 -s /desktop/gnome/url-handlers/oerp/enabled true -t bool
