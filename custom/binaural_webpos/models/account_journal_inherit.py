# -*- coding: utf-8 -*-
from odoo import api, fields, models

class binaural_account_journal(models.Model):
    _inherit = 'account.journal'
    _description = 'Herencia paara agregar informacion de tipo de pago para webpos'

    tipo_pago_webpos = fields.Char(string="Tipo pago webpos",size=2)
    