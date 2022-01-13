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
        14, 2), compute="_compute_negative_plus_rubber_cost")

    paper_cost = fields.Float(string="Costo de Papel", digits=(
        14, 2), compute="_compute_paper_cost")

    handm_cost = fields.Float(string="Costo H/M", digits=(14, 6))
    print_cost = fields.Float(string="Costo de Impresión", digits=(
        14, 2), compute="_compute_print_cost")

    coiling_cost = fields.Float(string="Costo de Embobinado", digits=(
        14, 2), compute="_compute_coiling_cost")

    packing_cost = fields.Float(string="Costo de Empaquetado", digits=(
        14, 2), compute="_compute_packing_cost")
    @api.model
    def create(self, vals):
        rubber = 0
        negative = 0
        coil = 0
        bushing = 0
        res = super().create(vals)
        for material in res.materials_lines_id:
            # Check if a clisse has more than one material with the name "Caucho".
            if bool(material.product_id) and \
               material.product_id.name.lower() == "caucho":
                rubber += 1
            if rubber > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un producto con el nombre Caucho.")

            # Check if a clisse has more than one material with the name "Negativo".
            if bool(material.product_id) and \
               material.product_id.name.lower() == "negativo":
                negative += 1
            if negative > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un producto con el nombre Caucho.")

            # Check if a clisse has more than one material with the "Bobina" category.
            if bool(material.product_id.categ_id) and \
               material.product_id.categ_id.name.lower() == "bobina":
                coil += 1
            if coil > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de una bobina como material.")

            # Check if a clisse has more than one material with the "Buje" category.
            if bool(material.product_id.categ_id) and \
               material.product_id.categ_id.name.lower() == "buje":
                bushing += 1
                # Calculate the bushing quantity
                if bool(res.labels_per_roll):
                    material.qty = res.quantity / res.labels_per_roll
            if bushing > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un buje como material.")
        return res

    @api.onchange("materials_lines_id")
    def _onchange_materials_lines_id(self):
        rubber = 0
        negative = 0
        coil = 0
        bushing = 0
        for material in self.materials_lines_id:
            # Check if a clisse has more than one material with the name "Caucho".
            if bool(material.product_id) and \
               material.product_id.name.lower() == "caucho":
                rubber += 1
            if rubber > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un producto con el nombre Caucho.")

            # Check if a clisse has more than one material with the name "Negativo".
            if bool(material.product_id) and \
               material.product_id.name.lower() == "negativo":
                negative += 1
            if negative > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un producto con el nombre Caucho.")
 
            # Check if a clisse has more than one material with the "Bobina" category.
            if bool(material.product_id.categ_id) and \
               material.product_id.categ_id.name.lower() == "bobina":
                coil += 1
            if coil > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de una bobina como material.")

            # Check if a clisse has more than one material with the "Buje" category.
            if bool(material.product_id.categ_id) and \
               material.product_id.categ_id.name.lower() == "buje":
                bushing += 1
                # Calculate the bushing quantity
                if bool(self.labels_per_roll):
                    material.qty = self.quantity / self.labels_per_roll
            if bushing > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un buje como material.")

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
                   material.product_id.categ_id.name.lower() == "bobina":
                    material_cost = material.cost
                    break
            clisse.paper_cost = (width * clisse.length_inches * material_cost * clisse.quantity) + \
                                (clisse.decrease * width / 1000 * material_cost)

    @api.depends("length_inches", "quantity", "materials_lines_id", "handm_cost")
    def _compute_print_cost(self):
        for clisse in self:
            total_colors = 0
            for product in clisse.materials_lines_id:
                if bool(product.product_id.categ_id) and \
                   product.product_id.categ_id.name.lower() == "tinta":
                    total_colors += 1
            clisse.print_cost = ((clisse.length_inches * 25.4 * clisse.quantity / 13.33) + (
                total_colors * 10)) * clisse.handm_cost + (total_colors * 2.4)

    @api.depends("materials_lines_id", "quantity")
    def _compute_coiling_cost(self):
        for clisse in self:
            cost = 0
            qty = 0
            for product in clisse.materials_lines_id:
                if bool(product.product_id.categ_id) and \
                   product.product_id.categ_id.name.lower() == "buje":
                    cost = product.cost
                    qty = product.qty
                    break
            clisse.coiling_cost = (cost * qty) + (qty * .1089)

    @api.depends("quantity")
    def _compute_packing_cost(selg):
        for clisse in self:
            clisse.packing_cost = clisse.quantity * .1
