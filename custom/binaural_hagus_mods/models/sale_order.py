from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    product_id = fields.Many2one(
        "product.product", compute="_compute_product_id")
    clisse_code = fields.Char(related="product_id.clisse_id.code")
    clisse_date = fields.Date(related="product_id.clisse_id.date")
    clisse_partner = fields.Char(
        string="Cliente", related="product_id.clisse_id.partner_id.name")
    clisse_troquel = fields.Char(
        string="Troquel", related="product_id.clisse_id.troquel_id.code")
    clisse_width_inches = fields.Float(
        related="product_id.clisse_id.width_inches")
    clisse_length_inches = fields.Float(
        related="product_id.clisse_id.length_inches")
    clisse_lines_width = fields.Integer(
        related="product_id.clisse_id.lines_width")
    clisse_labels_per_roll = fields.Float(
        related="product_id.clisse_id.labels_per_roll")
    clisse_size = fields.Char(related="product_id.clisse_id.size")
    clisse_background = fields.Char(related="product_id.clisse_id.background")
    clisse_orientation = fields.Char(
        string="Orientación", related="product_id.clisse_id.orientation_id.abbreviation")
    clisse_orientation_image = fields.Binary(
        related="product_id.clisse_id.orientation_image")
    clisse_finish_type = fields.Char(
        string="Acabado", related="product_id.clisse_id.finish_type_id.description")
    clisse_observations = fields.Text(
        related="product_id.clisse_id.observations")
    clisse_text = fields.Text(related="product_id.clisse_id.text")
    clisse_desing = fields.Binary(related="product_id.clisse_id.image_design")
    clisse_barcode = fields.Binary(
        related="product_id.clisse_id.image_barcode")
    clisse_description_label = fields.Text(
        related="product_id.clisse_id.description_label")
    clisse_state = fields.Selection(related="product_id.clisse_id.state")

    product_is_not_sticker = fields.Boolean(
        related="product_id.category_is_not_sticker", default=True)

    @api.model
    def create(self, vals):
        coil = 0
        bushing = 0

        res = super().create(vals)

        all_products = self.env["product.product"].search([])
        if not bool(all_products):
            raise UserError(
                "Antes de generar una orden de produccion deben existir productos.")

    @api.onchange("order_line")
    def _onchange_order_line(self):
        if not self.product_is_not_sticker:
            raise UserError(
                "No se pueden agregar mas productos a la orden de venta de un clisse.")

    @api.depends("order_line")
    def _compute_product_id(self):
        all_products = self.env["product.product"].search([])
        if bool(all_products):
            self.product_id = all_products.mapped("id")[0]
        for order in self:
            product = order.order_line[0].product_id if bool(
                order.order_line) else None
            if product:
                order.product_id = product.id
