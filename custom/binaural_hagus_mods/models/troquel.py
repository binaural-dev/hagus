# -*- coding: utf-8 -*-
import logging
import requests
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class HagusTroquel(models.Model):
	_name = 'hagus.troquel'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'code'

	code = fields.Char(string='Código')
	teeth = fields.Integer(string='Dientes', required=True)
	cylinders = fields.Integer(string='Cilindros')

	width_inches = fields.Float(string='Ancho(Pulgadas)')
	width_inches_uom = fields.Many2one('uom.uom', string='Medida',
        domain="[('category_id', '=', 4)]")
	variable = fields.Boolean(string='Variable')

	width_millimeters = fields.Float(string='Ancho(Milimetros)')
	width_millimeters_uom = fields.Many2one('uom.uom', string='Medida',
        domain="[('category_id', '=', 4)]")

	length_inches = fields.Float(string='Largo(Pulgadas)')
	length_inches_uom = fields.Many2one('uom.uom', string='Medida',
        domain="[('category_id', '=', 4)]")

	length_millimeters = fields.Float(string='Largo(Milimetros)')
	length_millimeters_uom = fields.Many2one('uom.uom', string='Medida',
        domain="[('category_id', '=', 4)]")

	paper_cut_centimeters = fields.Float(string='Ancho de Corte(centimetros)')
	paper_cut_centimeters_uom = fields.Many2one(
        'uom.uom', string='Medida',
        domain="[('category_id', '=', 4)]",
        default=lambda self: self.env['uom.uom'].search([('name', '=', u'cm')]).id)
	paper_cut_inches = fields.Float(string='Ancho de Corte(milimetros)')
	paper_cut_inches_uom = fields.Many2one(
        'uom.uom', string='Medida',
        domain="[('category_id', '=', 4)]")


	lines_width = fields.Integer(string='Lineas x ancho')
	repetition = fields.Integer(string='Repetición', required=True)
	designed = fields.Char(string='Diseñado')
	length_at_100 = fields.Float(string='Largo al 100%(mm)')
	reduction = fields.Float(string='% Reducción')
	final_size = fields.Float(string='Tamaño Final(mm)')
	active = fields.Boolean(string='Activo', default=True)
