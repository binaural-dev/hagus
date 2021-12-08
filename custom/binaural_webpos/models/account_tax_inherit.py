# -*- coding: utf-8 -*-
from odoo import api, fields, models

class binaural_account_journal(models.Model):
    _inherit = 'account.tax'
    _description = 'Herencia paara agregar informacion de impuesto para webpos'

    tipo_impuesto_webpos = fields.Char(string="Tipo impuesto webpos",size=1)
    