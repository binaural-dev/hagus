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

    def xml_factura(self, obj):
        if obj:
            root = etree.Element('FiscalDoc')
            doc = etree.ElementTree(root)

            #subelementos
            etree.SubElement(root, 'PrintStationId').text = obj['print_station_id']
            etree.SubElement(root, 'PrinterId').text = obj['printer_id']
            etree.SubElement(root, 'DocType').text = self._prefijo_factura
            etree.SubElement(root, 'DocNumber').text = obj['num_factura']
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
                        
                        
                    

            # Save to XML file
            outFile = open('/mnt/custom-addons/binaural_webpos/utils/' + self._prefijo_factura + 'output.xml', 'wb')
            doc.write(outFile, xml_declaration=True, encoding='utf-8', pretty_print=True) 

def main():
    XmlInteface().xml_factura({
       'print_station_id' : '1',
       'printer_id':'2',
       'num_factura':'001',
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
       }]
    })

if __name__ == "__main__":
    main()