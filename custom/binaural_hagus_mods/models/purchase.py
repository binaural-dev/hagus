from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    coil_cut_width_inches = fields.Float(related="product_id.cut_width_inches", store=True, readonly=False)
    msi = fields.Float(
        string="Medida MSI", compute="_compute_msi", inverse="_inverse_msi")
    product_category_name = fields.Char(related="product_id.categ_id.name")

    @api.depends("product_qty", "coil_cut_width_inches")
    def _compute_msi(self):
        self.msi = 0
        for order in self:
            if bool(order.product_qty) and bool(order.product_id.cut_width_inches):
                order.msi = order.product_qty * order.coil_cut_width_inches * 0.012

    def _inverse_msi(self):
        self.product_qty = 0
        for order in self:
            if bool(order.msi) and bool(order.product_id.cut_width_inches):
                order.product_qty = order.msi / (order.coil_cut_width_inches * 0.012)
