from odoo import api, fields, models


class ClisseSales(models.Model):
    """Clisse functionality related to Sales."""
    _inherit = "hagus.clisse"

    rubber_cost = fields.Float(string="Costo de Caucho", digits=(
        14, 2), compute="_compute_rubber_cost")
    negative_cost = fields.Float(string="Costo del Negativo", digits=(
        14, 2), compute="_compute_negative_cost")
    negative_plus_rubber_cost = fields.Float(string="Costo Negativo / Caucho", digits=(
        14, 2), compute="_compute_negative_per_rubber_cost")

    @api.depends("width_inches", "length_inches", "materials_lines_id")
    def _compute_rubber_cost(self):
        for clisse in self:
            total_colors = 0
            rubber = 1.05
            for product in clisse.materials_lines_id:
                if product.product_id.categ_id.name == "Tinta":
                    total_colors += 1
                if product.product_id.name == "Caucho":
                    rubber = product.cost
            clisse.rubber_cost = clisse.width_inches * \
                clisse.length_inches * total_colors * rubber

    @api.depends("width_inches", "length_inches", "materials_lines_id")
    def _compute_negative_cost(self):
        for clisse in self:
            total_colors = 0
            negative = .1
            for product in clisse.materials_lines_id:
                if product.product_id.categ_id.name == "Tinta":
                    total_colors += 1
                if product.product_id.name == "Negativo":
                    negative = product.cost
            clisse.negative_cost = clisse.width_inches * \
                clisse.length_inches * total_colors * negative

    @api.depends("negative_cost", "rubber_cost")
    def _compute_negative_plus_rubber_cost(self):
        for clisse in self:
            clisse.negative_plus_rubber_cost = clisse.negative_cost + \
                clisse.rubber_cost
