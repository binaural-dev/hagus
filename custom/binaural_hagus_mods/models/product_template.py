from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    clisse_id = fields.Many2one("hagus.clisse", string="Clisse")
    category_is_not_sticker = fields.Boolean(
        string="La categoria es Calcomanía o Etiqueta",
        compute="_compute_category_is_not_sticker")

    @api.depends("categ_id.name")
    def _compute_category_is_not_sticker(self):
        for product in self:
            category_name = product.categ_id.name
            if type(category_name) == str:
                if product.categ_id.name.lower() in ("calcomanía", "calcomania", "etiqueta"):
                    product.category_is_not_sticker = False
                    return
            product.category_is_not_sticker = True

    @api.model
    def create(self, vals):

        """
        Verificar que tanto "Negativo" como "Caucho" no se puedan crear dos veces.
        Estos son productos generados al instalar el modulo que son necesarios para
        el correcto funcionamiento del mismo.
        """
        if vals["name"].lower() == "negativo" and \
                bool(self.env["product.template"].search([("name", '=', "Negativo")])):
            raise ValidationError(
                "Este producto ya existe, si quiere modificar su costo debe editarlo.")
        if vals["name"].lower() == "caucho" and \
                bool(self.env["product.template"].search([("name", '=', "Caucho")])):
            raise ValidationError(
                "Este producto ya existe, si quiere modificar su costo debe editarlo.")

        res = super().create(vals)
        return res

class ProductCategory:
    _inherit = "product.category"

    @api.model
    def create(self, vals):
        if bool(self.env["product.category"].search([("name", '=', vals["name"])])):
            raise ValidationError(
                "No se puede crear la misma categoria dos veces.")
        res = super().create(vals)
        return res
