FIELD STYLE
===========

OpenERP module that allows to specify different colors or CSS class per field in view definition.

Three new attributes will be available on the field element of a view::

    - `bgcolor` for setting the background color
    - `fgcolor` for setting the foreground color (basically the text)
    - `ccsclass` for setting a custom CSS class to be applied on the field

`bg/fgcolor` are very useful for people that only want to change some field color without
having to deal with CSS, while `cssclass` is useful for assigning the same styles to a group of fields.

NOTE: you must apply a simple patch to this server's file

    `server/openerp/addons/base/rng/view.rng`

Just use the patch provided by this module (see server-view.rng.patch in the root of the package).