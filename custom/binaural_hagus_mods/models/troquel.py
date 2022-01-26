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
    teeth = fields.Integer(string='Dientes', required=True, default=1)
    cylinders = fields.Integer(string='Cilindros')

    width_inches = fields.Float(string='Ancho(Pulgadas)')
    width_inches_uom = fields.Many2one('uom.uom', string='Medida',
                                       domain="[('category_id', '=', 4)]")
    variable = fields.Boolean(string='Variable')

    width_millimeters = fields.Float(string='Ancho(Milimetros)', store=True,
                                     compute="_compute_width_millimeters",
                                     inverse="_inverse_width_millimeters")
    width_millimeters_uom = fields.Many2one('uom.uom', string='Medida',
                                            domain="[('category_id', '=', 4)]")

    length_inches = fields.Float(string='Largo(Pulgadas)')
    length_inches_uom = fields.Many2one('uom.uom', string='Medida',
                                        domain="[('category_id', '=', 4)]")

    length_millimeters = fields.Float(string='Largo(Milimetros)', store=True,
                                      compute="_compute_length_millimeters",
                                      inverse="_inverse_length_millimeters")
    length_millimeters_uom = fields.Many2one('uom.uom', string='Medida',
                                             domain="[('category_id', '=', 4)]")

    paper_cut_centimeters = fields.Float(
        string='Ancho de Corte(centimetros)', store=True,
        compute="_compute_paper_cut_centimeters",
        inverse="_inverse_paper_cut_centimeters")
    paper_cut_centimeters_uom = fields.Many2one(
        'uom.uom', string='Medida',
        domain="[('category_id', '=', 4)]",
        default=lambda self: self.env['uom.uom'].search(
            [('name', '=', u'cm')]).id)
    paper_cut_inches = fields.Float(
        string='Ancho de Corte(pulgadas)', required=True, default=1)
    paper_cut_inches_uom = fields.Many2one(
        'uom.uom', string='Medida',
        domain="[('category_id', '=', 4)]")

    lines_width = fields.Integer(string='Lineas x ancho')
    repetition = fields.Integer(string='Repetición', required=True, default=1)
    designed = fields.Char(string='Diseñado')
    length_at_100 = fields.Float(string='Largo al 100%(mm)')
    reduction = fields.Float(string='% Reducción')
    final_size = fields.Float(string='Tamaño Final(mm)')
    active = fields.Boolean(string='Activo', default=True)

    @api.depends("width_inches")
    def _compute_width_millimeters(self):
        self.width_millimeters = 0
        for troquel in self:
            troquel.width_millimeters = troquel.width_inches * 25.4

    def _inverse_width_millimeters(self):
        self.width_inches = 0
        for troquel in self:
            troquel.width_inches = troquel.width_millimeters / 25.4

    @api.depends("length_inches")
    def _compute_length_millimeters(self):
        self.length_millimeters = 0
        for troquel in self:
            troquel.length_millimeters = troquel.length_inches * 25.4

    def _inverse_length_millimeters(self):
        self.length_inches = 0
        for troquel in self:
            troquel.length_inches = troquel.length_millimeters / 25.4

    @api.depends("paper_cut_inches")
    def _compute_paper_cut_centimeters(self):
        self.paper_cut_centimeters = 0
        for troquel in self:
            troquel.paper_cut_centimeters = troquel.paper_cut_inches * 2.54

    def _inverse_paper_cut_centimeters(self):
        self.paper_cut_inches = 0
        for troquel in self:
            troquel.paper_cut_inches = troquel.paper_cut_centimeters / 2.54
