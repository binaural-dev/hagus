# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.addons.account_edi_extended.models.account_edi_document import DEFAULT_BLOCKING_LEVEL
from psycopg2 import OperationalError
import logging

_logger = logging.getLogger(__name__)


class binaural_account_edi_document(models.Model):
    _inherit = 'account.edi.document'
    _description = 'Herencia de documento electronico para account.move'

    state = fields.Selection([('to_send', 'To Send'), ('sent', 'Sent'), ('to_cancel', 'To Cancel'), ('cancelled', 'Cancelled'),('to_pay','To pay')])

    # def write(self, vals):
    #     _logger.info('===========================================')
    #     _logger.info(vals)
    #     super(binaural_account_edi_document,self).write(vals)        