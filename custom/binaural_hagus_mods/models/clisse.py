# -*- coding: utf-8 -*-
import logging
import requests
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class HagusClisse(models.Model):
    _name = 'hagus.clisse'
    _description = 'Clisse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'

    code = fields.Char(
        string='Código', copy=False, readonly=True,
        index=True, default=lambda self: _('New'))  # usar secuencia
    active = fields.Boolean(string='Activo',default=True)
    description = fields.Char(string='Descripción', required=True)
    date = fields.Date(
        string='Fecha', default=fields.Date.context_today, required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente',
                                 domain="[('active', '=',True)]")  # filtrar solo clientes
    troquel_id = fields.Many2one(
        'hagus.troquel', string='Troquel', domain="[('active', '=',True)]", required=True)
    width_inches = fields.Float(
        string='Ancho(Pulgadas)', related="troquel_id.width_inches")
    length_inches = fields.Float(
        string='Largo(Pulgadas)', related="troquel_id.length_inches")
    labels_per_roll = fields.Float(
        string='Etiquetas por Rollo', digits=(10, 2), required=True)

    size = fields.Char(string='Tamaño')
    background = fields.Char(string='Fondo')

    orientation_id = fields.Many2one('hagus.orientation', string='Orientación')
    orientation_image = fields.Binary(related="orientation_id.files")
    finish_type_id = fields.Many2one('hagus.finish.types', string='Acabado')

    observations = fields.Text(string='Obervaciones')
    text = fields.Text(string='Texto')

    image_design = fields.Binary("Diseño")
    design_filename = fields.Char()
    image_barcode = fields.Binary("Código de Barras")
    barcode_filename = fields.Char()
    description_label = fields.Text(string='Descripción de la etiqueta')

    materials_lines_id = fields.One2many(
        'hagus.clisse.line', 'clisse_id', string='Lineas materiales')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('production', 'En Producción')],
        'Estado', default="draft")

    payment_method_id = fields.Many2one(
        "account.payment.method", string="Tipo de Pago",
        domain="[('payment_type', '=', 'inbound')]")
    payment_term = fields.Many2one(
        "account.payment.term", string="Plazo de Pago")

    @api.model
    def create(self, vals):
        # Set Code
        if vals.get('code', _('New')) == _('New'):
            seq_date = None
            if 'date' in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['date']))
            vals['code'] = self.env['ir.sequence'].next_by_code(
                'hagus.clisse', sequence_date=seq_date) or _('New')

        return super().create(vals)
