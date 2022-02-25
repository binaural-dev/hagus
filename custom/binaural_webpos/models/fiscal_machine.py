# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)

class binaural_fiscal_machine(models.Model):
    _name = 'binaural.mfwebpos'
    _description = 'Maestro de maquina fiscal'

    name = fields.Char(string='Identificador de la maquina', required=True)
    serial_machine = fields.Char(string='Serial de la maquina fiscal')
    serial_brand = fields.Char(string='Marca')
    default_machine = fields.Boolean(string='Impresora por defecto en facturacion')       

    @api.model_create_multi
    def create(self, vals_list):        
        default_search = self.env['binaural.mfwebpos'].search([('default_machine','=',True)], limit = 1)    
        result = ''
        for val in vals_list:
            if val['default_machine'] == True and len(default_search) > 0:
                raise ValidationError('Ya existe una maquina con valor por defecto asignada, no puede tener 2 maquinas por defecto')            
                return False;    
            else:
                result = super(binaural_fiscal_machine, self).create(val)                
                    
        return result

    def write(self, vals):        
        default_search = self.env['binaural.mfwebpos'].search([('default_machine','=',True)], limit = 1)    
        result = ''
        if vals['default_machine'] == True and len(default_search) > 0:
            raise ValidationError('Ya existe una maquina con valor por defecto asignada, no puede tener 2 maquinas por defecto')            
            return False;
        else:            
            result = super(binaural_fiscal_machine, self).write(vals)

        return result
            
    _sql_constrains = [
        ('unique_name_mf','UNIQUE (name)','Ya existe un identificador de la maquina con el mismo nombre')        
    ]
        