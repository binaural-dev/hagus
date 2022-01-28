from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    clisse_id = fields.Many2one("hagus.clisse", string="Clisse")
    category_is_not_sticker = fields.Boolean(
        string="La categoria es Calcomanía o Etiqueta",
        compute="_compute_category_is_not_sticker")
    cut_width_inches = fields.Float(
        "Ancho de Corte (Pulgadas)", digits=(14, 2), default=1)
    msi = fields.Float(string="Medida MSI", digits=(
        14, 4), compute="_compute_msi")
    category_name = fields.Char(
        string="Nombre de la categoria", related="categ_id.name")

    @api.depends("categ_id.name")
    def _compute_category_is_not_sticker(self):
        for product in self:
            category_name = product.categ_id.name
            if type(category_name) == str:
                if product.categ_id.name.lower() in ("calcomanía", "calcomania", "etiqueta"):
                    product.category_is_not_sticker = False
                    return
            product.category_is_not_sticker = True

    @api.depends("qty_available", "cut_width_inches")
    def _compute_msi(self):
        for product in self:
            total_ft = product.qty_available
            product.msi = product.cut_width_inches * total_ft * 0.012


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.model
    def create(self, vals):
        if bool(self.env["product.category"].search([("name", '=', vals["name"])])):
            raise ValidationError(
                "No se puede crear la misma categoria dos veces.")
        res = super().create(vals)
        return res
