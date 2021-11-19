# -*- coding: utf-8 -*-
import logging
import requests
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class HagusClisse(models.Model):
	_name = 'hagus.clisse'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'code'

	code = fields.Char(string='Código')#usar secuencia
	description = fields.Char(string='Descripción')
	date = fields.Date(string='Fecha')#tomar del dia
	partner_id = fields.Many2one('res.partner', string='Cliente') #filtrar solo clientes
	troquel_id = fields.Many2one('hagus.troquel', string='Troquel')# filtrar activos
	width_inches = fields.Float(string='Ancho(Pulgadas)',related="troquel_id.width_inches")
	width_inches_uom = fields.Many2one('uom.uom', string='Medida',related="troquel_id.width_inches_uom")
	length_inches = fields.Float(string='Largo(Pulgadas)',realted="troquel_id.length_inches")
	length_inches_uom = fields.Many2one('uom.uom', string='Medida',realted="troquel_id.length_inches_uom")
	lines_width = fields.Integer(string='Lineas x ancho',related="troquel_id.lines_width")
	labels_per_roll = fields.Float(string='Etiquetas por Rollo', digits=(10, 2))

	size = fields.Char(string='Tamaño')
	botton = fields.Char(string='Fondo')

	orientation_id = fields.Many2one('hagus.orientation', string='Orientación')
	finish_type_id = fields.Many2one('hagus.finish.types', string='Acabado')

	observations = fields.Text(string='Obervaciones')
	text = fields.Text(string='Texto')


	#duda si dejarlos imagen o binary
	"""design = fields.Binary(string='Diseño')
	design_filename = fields.Char(string='Diseño')

	barcode = fields.Binary(string='Código de Barras')
	barcode_filename = fields.Char(string='Código de Barras')"""
	"""Ancho de corte (cm) que realice la conversión de cm a pulgadas y viceversa
	Ancho de corte (pulg) que realice la conversión de cm a pulgadas y viceversa
	Etiquetas por Rollo
	Fondo"""

	image_design = fields.Image("Diseño")
	image_barcode = fields.Image("Código de Barras")
	description_label = fields.Text(string='Descripción de la etiqueta')


	materials_lines_id = fields.One2many('hagus.clisse.line', 'clisse_id', string='Lineas materiales')

	state = fields.Selection([
		('draft', 'Borrador'),
		('open', 'Abierto'),
		('cancel', 'Cancelado'),
	], string='Estado')

class HagusClisseLines(models.Model):
	_name = 'hagus.clisse.line'
	_rec_name = 'product_id'
	product_id = fields.Many2one('product.product', string='Producto') #ojo con product template
	description = fields.Char(string='Descripción')
	qty = fields.Float(string='Cantidad', digits=(16, 2))
	cost = fields.Float(string='Costo', digits=(16, 3))
	clisse_id = fields.Many2one('hagus.clisse', string='Clisse asociado')