from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    msi = fields.Float(string="Medida MSI", digits=(14,6), related="product_id.msi")

