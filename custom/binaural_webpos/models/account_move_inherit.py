# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
from odoo.addons.binaural_webpos.utils.xml_base import XmlInterface

_logger = logging.getLogger(__name__)


class binaural_account_move(models.Model):
    _inherit = 'account.move'
    _description = 'Herencia para editar el post de la factura para faturacion electronica'

    fiscal_number = fields.Char(string="Numero fiscal", help="Numero devuelto por la maquina fiscal una vez impresa la factura", index=True, copy=False) #readonly=True
    fiscal_machine_id = fields.Many2one('binaural.mfwebpos', string='Maquina fiscal asociada', required=True, 
        default=(lambda self:self.env['binaural.mfwebpos'].search([('default_machine','=',True)], limit=1)))

    aditional_info_invoice_header1 = fields.Char(string='Informacion adicional factura (cabecera 1)', size=80, copy=False)
    aditional_info_invoice_header2 = fields.Char(string='Informacion adicional factura (cabecera 2)', size=80, copy=False)

    aditional_info_invoice_tailer1 = fields.Char(string='Informacion adicional factura (pie 1)', size=80, copy=False)
    aditional_info_invoice_tailer2 = fields.Char(string='Informacion adicional factura (pie 2)', size=80, copy=False)    

    def print_invoice(self):
        invoice = self.env['account.move'].browse(self.id)        
        
        # factura
        if invoice.move_type == 'out_invoice' and invoice.debit_origin_id.id == False:            
            xml_content, xml_name = XmlInterface().build_xml_to_print(invoice, XmlInterface()._prefijo_factura)
        # nota de credito
        elif invoice.move_type == 'out_refund':            
            xml_content, xml_name = XmlInterface().build_xml_to_print(invoice, XmlInterface()._prefijo_nota_credito)
        # nota de debito
        elif invoice.move_type == 'out_invoice' and invoice.debit_origin_id.id != False:            
            xml_content, xml_name = XmlInterface().build_xml_to_print(invoice, XmlInterface()._prefijo_nota_debito)

        XmlInterface().xml_print_to_std(xml_content)