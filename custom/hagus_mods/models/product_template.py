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
                if product.categ_id.name.lower() in ("calcomanía", "calcomania" , "etiqueta"):
                    product.category_is_not_sticker = False
                    return
            product.category_is_not_sticker = True

    @api.model
    def create(self, vals):
        if vals["name"].lower() == "negativo" and \
            bool(self.env["product.template"].search([("name", '=', "Negativo")])):
            raise ValidationError("Este producto ya existe, si quiere modificar su costo debe editarlo.")
        if vals["name"].lower() == "caucho" and \
            bool(self.env["product.template"].search([("name", '=', "Caucho")])):
            raise ValidationError("Este producto ya existe, si quiere modificar su costo debe editarlo.")
            
        return super().create(vals)

