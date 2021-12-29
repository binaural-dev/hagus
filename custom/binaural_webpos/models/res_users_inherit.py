# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)

class binaural_res_users(models.Model):
    _inherit = 'res.users'
    _description = 'Herencia para agregar ID de estacion de impresion'

    print_station_id = fields.Char(string="Estacion de impresion por usuario", size=2)

    _sql_constraints = [
        ('unique_print_station_id','UNIQUE (print_station_id)', 'Ya existe un usuario con este ID de estacion de impresora fiscal')
    ]