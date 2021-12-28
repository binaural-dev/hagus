from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_repr
from odoo.exceptions import UserError
from odoo.addons.binaural_webpos.utils.xml_base import XmlInterface

from lxml import etree
import base64
import logging

_logger = logging.getLogger(__name__)

DEFAULT_FACTURX_DATE_FORMAT = '%Y%m%d'

class binaural_account_edi_format(models.Model):
    _inherit = 'account.edi.format'
    _description = 'EDI format inherit to webpos'

    # prefijos
    _prefijo_factura = 'F'
    _prefijo_nota_credito = 'C'
    _prefijo_nota_debito = 'D'
    _prefijo_no_fiscal = 'N'
    encoding_xml = 'UTF-8'

    # metodo para limpiar string
    def _sanitize_string(self,cadena):
        html_escape_table = {
            "&" : "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">" : "&gt;",
            "<" : "&lt;",
        }
        
        return escape(cadena, html_escape_table)

    def _is_compatible_with_journal(self, journal):
        self.ensure_one()
        res = super()._is_compatible_with_journal(journal)
        if self.code != 'facturx_pa':
            return res
        return journal.type == 'sale'

    def _post_invoice_edi(self, invoices, test_mode=False):
        self.ensure_one()
        if self.code != 'facturx_pa':            
            return super()._post_invoice_edi(invoices, test_mode=test_mode)
        res = {}
        for invoice in invoices:                   
            if invoice.invoice_payments_widget != 'false': #solucion temporal porque se crea el edi document sin pagos, TODO: permitir llamar a la misma funcion con o sin pagos
                xml_content, xml_file = XmlInterface().build_xml_to_print(invoice,'F') #hacer if con tipo de documento, por defecto envio factura
                res[invoice] = {'attachment': XmlInterface().xml_print_to_file(xml_content,xml_file,invoice)}
        return res
    
    #DEPRECATED: reemplazada por funcion build_xml_to_print en utils
    def _export_facturx(self, invoice):
    
        def format_date(dt):
            # Format the date in the Factur-x standard.
            dt = dt or datetime.now()
            return dt.strftime(DEFAULT_FACTURX_DATE_FORMAT)

        def format_monetary(number, currency):
            # Format the monetary values to avoid trailing decimals (e.g. 90.85000000000001).            
            return float_repr(number, currency.decimal_places)            

        self.ensure_one()    

        # Create file content.
        template_values = {
            'record': invoice,
            'format_date': format_date,
            'format_monetary': format_monetary,
            'invoice_line_values': [],
        }

        # Tax lines.
        aggregated_taxes_details = {line.tax_line_id.id: {
            'line': line,
            'tax_amount': -line.amount_currency if line.currency_id else -line.balance,
            'tax_base_amount': 0.0,
        } for line in invoice.line_ids.filtered('tax_line_id')}

        # Invoice lines.
        for i, line in enumerate(invoice.invoice_line_ids.filtered(lambda l: not l.display_type)):
            price_unit_with_discount = line.price_unit * (1 - (line.discount / 100.0))
            taxes_res = line.tax_ids.with_context(force_sign=line.move_id._get_tax_force_sign()).compute_all(
                price_unit_with_discount,
                currency=line.currency_id,
                quantity=line.quantity,
                product=line.product_id,
                partner=invoice.partner_id,
                is_refund=line.move_id.move_type in ('in_refund', 'out_refund'),
            )
            
            line_template_values = {
                'line': line,
                'index': i + 1,
                'format_discount': str(line.discount) + '%',
                'tax_details': {},
                'net_price_subtotal': taxes_res['total_excluded'],
            }

            #se iterara una sola vez asumiendo que cada producto tiene un solo impuesto (preguntar a Maria)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])                

                #diccionario por lista
                tax_details = {
                    'tax': tax,
                    'tax_webpos': tax.tipo_impuesto_webpos,
                    'tax_amount': tax_res['amount'],
                    'tax_base_amount': tax_res['base'],
                }

                line_template_values['tax_details'] = tax_details                

                if tax.id in aggregated_taxes_details:
                    aggregated_taxes_details[tax.id]['tax_base_amount'] += tax_res['base']

                break #una sola iteracion

            template_values['invoice_line_values'].append(line_template_values)

        template_values['tax_details'] = list(aggregated_taxes_details.values())

        xml_content = b"<?xml version='1.0' encoding='UTF-8'?>"
        xml_content += self.env.ref('binaural_webpos.binaural_webpos_xml_template')._render(template_values)
        xml_name = self._prefijo_factura + '%s.xml' % (invoice.name.replace('/', '_'))
        return self.env['ir.attachment'].create({
            'name': xml_name,
            'datas': base64.encodebytes(xml_content),
            'mimetype': 'application/xml'
        })