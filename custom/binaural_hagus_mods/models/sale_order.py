from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    product_id = fields.Many2one(
        "product.product", compute="_compute_product_id", store=True)
    clisse_ids = fields.Many2many("hagus.clisse")
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
        related="product_id.product_tmpl_id.category_is_not_sticker")

    more_than_one_clisse = fields.Boolean(compute="_compute_more_than_one_clisse")

    @api.model
    def create(self, vals):
        res = super().create(vals)

        all_products = self.env["product.product"].search([])
        if not bool(all_products):
            raise UserError(
                "Antes de generar una orden de venta deben existir productos.")
        # Agregando cada uno de los clisse de la orden de venta a la lista de clisse.
        for product in res.order_line.mapped("product_id"):
            if not product.category_is_not_sticker:
                res.clisse_ids += product.product_tmpl_id.clisse_id
        return res
    
    def write(self, vals):
        res = super().write(vals)
        # Agregando la orden de venta a la lista de ordenes de venta de cada uno de los
        # clisse cuyo producto forma parte de la misma.
        for clisse in self.clisse_ids:
            if self.id not in clisse.mapped("sale_order_ids.id"):
                clisse.sale_order_ids += self.env["sale.order"].search([("id", '=', self.id)])
        return res
    
    @api.onchange("order_line")
    def _onchange_sale_order(self):
        for clisse in self.clisse_ids:
            self.write({"clisse_ids": [(3, clisse.id)]})

        for product in self.order_line.mapped("product_id"):
            clisse_id = product.product_tmpl_id.clisse_id
            if clisse_id not in self.clisse_ids:
                self.clisse_ids += clisse_id

    @api.depends("order_line")
    def _compute_product_id(self):
        if len(self.order_line) > 0:
            self.product_id = self.order_line[0].product_id.id
        else:
            self.product_id = None
        for order in self:
            for line in order.order_line:
                if not line.product_id.product_tmpl_id.category_is_not_sticker:
                    order.product_id = line.product_id.id
                    return

    @api.depends("order_line", "clisse_ids")
    def _compute_more_than_one_clisse(self):
        for order in self:
            if len(order.clisse_ids) > 1:
                order.more_than_one_clisse = True
            else:
                order.more_than_one_clisse = False
