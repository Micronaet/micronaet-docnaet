# Copyright 2019  Micronaet SRL (<http://www.micronaet.it>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import sys
import logging
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo import exceptions


_logger = logging.getLogger(__name__)


class DocnaetDocument(models.Model):
    """ Add extra fields for integrare a link to docnaet document
    """
    _inherit = 'docnaet.document'

    import_date = fields.Datetime('Import date', default=fields.Datetime.now())
    uploaded = fields.Boolean('Uploaded')

