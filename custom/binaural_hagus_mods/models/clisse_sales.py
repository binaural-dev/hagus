import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class ClisseSales(models.Model):
    """Clisse functionality related to Sales."""
    _inherit = "hagus.clisse"

    quantity = fields.Integer(string="Cantidad a Producir")
    decrease = fields.Float(string="Merma", digits=(14, 5))

    rubber_cost = fields.Float(string="Costo de Caucho", digits=(
        14, 2), compute="_compute_rubber_cost")
    negative_cost = fields.Float(string="Costo del Negativo", digits=(
        14, 2), compute="_compute_negative_cost")
    negative_plus_rubber_cost = fields.Float(string="Costo Negativo / Caucho", digits=(
        14, 2), compute="_compute_negative_per_rubber_cost")

    paper_cost = fields.Float(string="Costo de Papel", digits=(
        14, 2), compute="_compute_paper_cost")

    @api.model
    def create(self, vals):
        # Check if a clisse has more than one "Bobina" material category.
        coil = 0
        res = super().create(vals)
        for material in res.materials_lines_id:
            if material.product_id.categ_id.name.lower() == "buje":
                coil += 1
            if coil > 1:
                raise ValidationError("Un clisse no puede tener más de una bobina como material.")
        return res

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

    @api.depends("width_inches", "length_inches", "materials_lines_id", "quantity", "decrease")
    def _compute_paper_cost(self):
        for clisse in self:
            material_cost = 0
            width = clisse.width_inches
            for material in clisse.materials_lines_id:
                if bool(material.product_id.categ_id.name) and \
                   material.product_id.categ_id.name.lower() == "buje":
                    material_cost = material.cost
                    break
            clisse.paper_cost = (width * clisse.length_inches * material_cost * clisse.quantity) + \
                                (clisse.decrease * width / 1000 * material_cost)
