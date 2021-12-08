from xml.sax.saxutils import escape
from lxml import etree

class XmlInteface():
    _prefijo_factura = 'F'
    _prefijo_nota_credito = 'C'
    _prefijo_nota_debito = 'D'
    _prefijo_no_fiscal = 'N'
    encoding_xml = 'UTF-8'

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

    def xml_factura_nota(self, obj):
        if obj:
            root = etree.Element('FiscalDoc')
            doc = etree.ElementTree(root)

            #subelementos
            etree.SubElement(root, 'PrintStationId').text = obj['print_station_id']
            etree.SubElement(root, 'PrinterId').text = obj['printer_id']
            if obj['tipo_documento']:                
                etree.SubElement(root, 'DocType').text = obj['tipo_documento']
            etree.SubElement(root, 'DocNumber').text = obj['num_factura']
            if obj['num_factura_nota']:
                etree.SubElement(root, 'InvoiceNumber').text = obj['num_factura_nota']            
            etree.SubElement(root, 'CustomerName').text = self._sanitize_string(obj['cliente'])
            etree.SubElement(root, 'CustomerRUC').text = obj['ruc']
            etree.SubElement(root, 'CustomerAddress').text = self._sanitize_string(obj['direccion_cliente'])
            etree.SubElement(root, 'Email').text = obj['email']

            #info extra que se imprime en el encabezado o pie de pagina
            if 'add_info' in obj:
                add_info = etree.SubElement(root, 'AddInfo')                                  
                for index, item in enumerate(obj['add_info']):
                    line = etree.SubElement(add_info,'Line')
                    line.set('Id',str(index+1))
                    if item[1]:
                        line.text = item[1]
                    
            if 'items' in obj:
                items = etree.SubElement(root,'Items')
                for items_factura in obj['items']:
                    linea_factura = etree.SubElement(items,'Item')
                    linea_factura.set('Id',items_factura['id'])
                    linea_factura.set('Price', items_factura['precio'])
                    linea_factura.set('Qty',items_factura['cantidad'])
                    linea_factura.set('Desc',items_factura['descripcion_producto'])
                    linea_factura.set('Tax',items_factura['impuesto'])
                    #0 si es exento,
                    #1 si marca 7% de ITBMS,
                    #2 si marca 10% de ITBMS (Licores)
                    #3 si marca 15% de ITBMS (Cigarrillos).
                    
                    linea_factura.set('Code',items_factura['codigo'])
                    if 'comentario' in items_factura:
                        linea_factura.set('Comments',items_factura['comentario'])
                    if 'porc_descuento' in items_factura:
                        linea_factura.set('dperc',items_factura['porc_descuento']) #00.00%
                    linea_factura.set('damt','0')
                                      
            # 01 equivale a Efectivo
            # 02 equivale a T.Crédito
            # 03 equivales a T.Débito
            # 04 equivale a Cheque
            # 05 equivale a Abono
            # 06 equivale a Certificado
            # 07 equivale a Nota de crédito ▪ 08 equivale a Crédito
            # 09 equivale a Transferencias
            # 10 equivale a Otros
            if 'pagos' in obj:
                payments = etree.SubElement(root,'Payments')                        
                for pago in obj['pagos']:
                    linea_pago = etree.SubElement(payments,'Payment')    
                    linea_pago.set('Id',pago['id'])
                    linea_pago.set('amt',pago['monto'])
                    linea_pago.set('type',pago['tipo'])
            
            if 'pie_pagina' in obj:
                pie_pagina = etree.SubElement(root,'Tailer')
                for index, item in enumerate(obj['pie_pagina']):
                    line = etree.SubElement(pie_pagina,'Line')
                    line.set('Id',str(index+1))
                    if item[1]:
                        line.text = item[1]                                        

            # Save to XML file            
            self._xml_print_to_file('/mnt/custom-addons/binaural_webpos/utils/',obj['tipo_documento'],doc)   
            
    def xml_nofiscal(self, obj):
        if obj:
            root = etree.Element('FiscalDoc')
            doc = etree.ElementTree(root)

            #subelementos
            etree.SubElement(root, 'PrintStationId').text = obj['print_station_id']
            etree.SubElement(root, 'PrinterId').text = obj['printer_id']
            if obj['tipo_documento']:                
                etree.SubElement(root, 'DocType').text = obj['tipo_documento']
            etree.SubElement(root, 'DocNumber').text = obj['num_factura']
            if obj['num_factura_nota']:
                etree.SubElement(root, 'InvoiceNumber').text = obj['num_factura_nota']            
            etree.SubElement(root, 'CustomerName').text = self._sanitize_string(obj['cliente'])
            etree.SubElement(root, 'CustomerRUC').text = obj['ruc']
            etree.SubElement(root, 'CustomerAddress').text = self._sanitize_string(obj['direccion_cliente'])
            etree.SubElement(root, 'Email').text = obj['email']

            #info extra que se imprime en el encabezado o pie de pagina
            if 'add_info' in obj:
                add_info = etree.SubElement(root, 'AddInfo')                                  
                for index, item in enumerate(obj['add_info']):
                    line = etree.SubElement(add_info,'Line')
                    line.set('Id',str(index+1))
                    if item[1]:
                        line.text = item[1]

            self._xml_print_to_file('/mnt/custom-addons/binaural_webpos/utils/',obj['tipo_documento'],doc)   

    def _xml_print_to_file(self, uri, tipo_documento, doc_root):
        outFile = open(uri + tipo_documento + 'output.xml', 'wb')
        doc_root.write(outFile, xml_declaration=True, encoding='utf-8', pretty_print=True)     

def main():
    XmlInteface().xml_factura_nota({
       'print_station_id' : '1',
       'printer_id':'2',
       'tipo_documento': 'C',
       'num_factura':'001',
       'num_factura_nota':'001',
       'cliente':'Manuel Guerrero',
       'ruc' : 'J-29532196',
       'direccion_cliente':'Carrera & entre < y >',
       'email':'manuelgc1201@gmail.com',
       'add_info': [(1,'otra info'),(2,''),(3,'mas info')],
       'items':[{
           'id': '01',
           'precio': '101.00',
           'cantidad':'2',
           'descripcion_producto':'audifonos',
           'impuesto':'1',
           'codigo':'001'           
       },{
           'id': '02',
           'precio': '250.00',
           'cantidad':'2',
           'descripcion_producto':'computadora',
           'impuesto':'1',
           'codigo':'002',
           'porc_descuento':'10.00%'
       }],
       'pagos':[{
           'id':'001',
           'monto':'26.66',
           'tipo':'01'
       },
       {
           'id':'002',
           'monto':'30.66',
           'tipo':'08'
       }],
       'pie_pagina':[(1,'otra info'),(2,''),(3,'mas info')]
    })

    XmlInteface().xml_nofiscal({
       'print_station_id' : '1',
       'printer_id':'2',
       'tipo_documento': 'N',
       'num_factura':'001',
       'num_factura_nota':'001',
       'cliente':'Manuel Guerrero',
       'ruc' : 'J-29532196',
       'direccion_cliente':'Carrera & entre < y >',
       'email':'manuelgc1201@gmail.com',
       'add_info': [(1,'otra info'),(2,''),(3,'mas info')]})

if __name__ == "__main__":
    main()