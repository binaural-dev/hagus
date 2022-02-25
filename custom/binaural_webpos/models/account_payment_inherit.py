# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class binaural_account_payment(models.Model):
    _inherit = 'account.payment'
    _description = 'Herencia de pagos para agregar tipo de pago'

    type_payment_id = fields.Many2one(comodel_name="tipopago.webpos", string="Tipo de pago", required=True)    