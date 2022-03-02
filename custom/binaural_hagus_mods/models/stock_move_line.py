from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"


    lot_product_qty = fields.Float(related="lot_id.product_qty")
