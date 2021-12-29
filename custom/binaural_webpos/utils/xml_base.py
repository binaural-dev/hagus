from odoo import models, fields, api
from xml.sax.saxutils import escape
from lxml import etree
import json
from suds.client import Client
from suds.xsd.doctor import ImportDoctor, Import

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_repr
import base64
import logging

_logger = logging.getLogger(__name__)

DEFAULT_FACTURX_DATE_FORMAT = '%Y%m%d'

class XmlInterface():
    _prefijo_factura = 'F'
    _prefijo_nota_credito = 'C'
    _prefijo_nota_debito = 'D'
    _prefijo_no_fiscal = 'N'
    encoding_xml = 'UTF-8'
    _url_test_soap = 'https://webpospanama.com/fptest/wsfprt.asmx?WSDL'
    _url_production_soap = 'https://ventas.webpospanana.com/wsfprt.asmx?WSDL'
    _url_schema_soap = 'http://www.w3.org/2001/XMLSchema'
    _url_schema_location_soap = 'http://www.w3.org/2001/XMLSchema.xsd'
    _url_namespace_soap = 'http://www.webpospanama.com/FPrint'
    #valor entregado por webpos, considerar agregarlo como modelo en odoo
    _company_id = '' 
    _user_webpos = ''
    _password_webpos = ''

    def __init__(self):
        pass

    def _sanitize_string(self,cadena):
        html_escape_table = {
            "&" : "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">" : "&gt;",
            "<" : "&lt;",
        }
        
        return escape(cadena, html_escape_table)

    def build_xml_to_print(self, invoice, type_document):

        def format_date(dt):
            # Format the date in the Factur-x standard.
            dt = dt or datetime.now()
            return dt.strftime(DEFAULT_FACTURX_DATE_FORMAT)

        def format_monetary(number, currency):
            # Format the monetary values to avoid trailing decimals (e.g. 90.85000000000001).            
            return float_repr(number, currency.decimal_places)            

        invoice.ensure_one()    

        #get notas de debito o credito
        origin_document = ''
        if type_document == self._prefijo_nota_credito and invoice.reversed_entry_id.id != False:
            origin_document = invoice.env['account.move'].search([('reversed_entry_id','=',invoice.reversed_entry_id.id)])
        elif type_document == self._prefijo_nota_debito and invoice.debit_origin_id != False:
            origin_document = invoice.env['account.move'].search([('debit_origin_id','=',invoice.debit_origin_id.id)])
        
        #get user login
        current_user_login = invoice.env['res.users'].browse(invoice._uid)

        # Create file content.
        template_values = {
            'record': invoice,
            'origin_document': origin_document,
            'type_document':type_document,
            'format_date': format_date,
            'format_monetary': format_monetary,
            'invoice_line_values': [],
            'payments':[],
            'current_user_login':current_user_login
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
                tax = invoice.env['account.tax'].browse(tax_res['id'])                

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

        # Payments
        payments = self._get_payments_invoice(invoice)
        if payments:            
            template_values['payments'] = payments

        template_values['tax_details'] = list(aggregated_taxes_details.values())

        xml_content = b"<?xml version='1.0' encoding='UTF-8'?>"
        xml_content += invoice.env.ref('binaural_webpos.binaural_webpos_xml_template')._render(template_values)                
        xml_name = type_document + '%s.xml' % (invoice.name.replace('/', '_'))        

        return xml_content, xml_name        

    def _get_payments_invoice(self, invoice):
        if invoice.invoice_payments_widget != False:
            payments_list = []
            payments_dict = json.loads(invoice.invoice_payments_widget)
            for payment in payments_dict["content"]:                
                pay = invoice.env['account.payment'].browse(payment["account_payment_id"])                
                payments_list.append(pay)                      
            return payments_list
        else:
            return False    

    def xml_print_to_file(self, content, file_name, invoice):          
        return invoice.env['ir.attachment'].create({
            'name':file_name,
            'datas': base64.encodebytes(content),
            'mimetype': 'application/xml'
        })

    def xml_print_to_std(self, content):
        _logger.info(content)
        return content

    def _connect_soap(self, test_mode=False):
        
        imp = Import(self._url_schema_soap, location=self._url_schema_location_soap)
        imp.filter.add(self._url_namespace_soap)
        doctor = ImportDoctor(imp)
        
        if test_mode:                              
            return Client(self._url_production_soap, doctor=doctor)
        else:            
            return Client(self._url_test_soap, doctor=doctor)
            

    def xml_to_service_mf(self, xml_content ,test_mode=False):
        client_soap = self._connect_soap(test_mode)        
        response = client_soap.service.SendxmlFileToPrint(xml_content.decode("utf-8"),self._user_webpos,self._password_webpos,self._company_id)

        print(response) #TODO: en espera de respuesta de Panama para terminar implementacion