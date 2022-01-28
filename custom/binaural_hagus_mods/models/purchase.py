from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    msi = fields.Float(
        string="Medida MSI", related="product_id.msi", readonly=False, store_true=True)
