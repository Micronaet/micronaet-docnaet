===========================
Create custom link in Gnome
===========================

https://support.shotgunsoftware.com/hc/en-us/articles/219031308-How-to-launch-external-applications-using-custom-protocols-rock-instead-of-http-

Registering a Protocol on Linux

gconftool-2 -t string -s /desktop/gnome/url-handlers/foo/command 'foo "%s"'
gconftool-2 -s /desktop/gnome/url-handlers/foo/needs_terminal false -t bool
gconftool-2 -s /desktop/gnome/url-handlers/foo/enabled true -t bool

Then put the settings from your local gconf file into the global defaults in:

/etc/gconf/gconf.xml.defaults/%gconf-tree.xml

This specifically mentions 64-bit but the same thing works on 32-bit as well. 
Also, even though the change is only in the Gnome settings, it also works for 
KDE because apparently Firefox/Iceweasel defers to gnome-open regardless of what window manager you are running when it encounters a prefix which it doesn't understand (such as foo://). So, other browsers, like Konqueror in KDE, won't work under this scenario.

See http://askubuntu.com/questions/527166/how-to-set-subl-protocol-handler-with-unity 
for more information on setting up protocol handlers for Action Menu Items in 
Ubuntu.

