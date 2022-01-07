from odoo import api, fields, models


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

