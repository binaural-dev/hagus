from odoo import fields, models, api
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    clisse_code = fields.Char(related="product_id.clisse_id.code")
    clisse_date = fields.Date(related="product_id.clisse_id.date")
    clisse_partner = fields.Char(
            string="Cliente", related="product_id.clisse_id.partner_id.name")
    clisse_troquel = fields.Char(
            string="Troquel", related="product_id.clisse_id.troquel_id.code")
    clisse_width_inches = fields.Float(related="product_id.clisse_id.width_inches")
    clisse_length_inches = fields.Float(related="product_id.clisse_id.length_inches")
    clisse_lines_width = fields.Integer(related="product_id.clisse_id.lines_width")
    clisse_labels_per_roll = fields.Float(related="product_id.clisse_id.labels_per_roll")
    clisse_size = fields.Char(related="product_id.clisse_id.size")
    clisse_background = fields.Char(related="product_id.clisse_id.background")
    clisse_orientation = fields.Char(
            string="Orientación", related="product_id.clisse_id.orientation_id.abbreviation")
    clisse_orientation_image = fields.Binary(related="product_id.clisse_id.orientation_image")
    clisse_finish_type = fields.Char(
            string="Acabado", related="product_id.clisse_id.finish_type_id.description")
    clisse_observations = fields.Text(related="product_id.clisse_id.observations")
    clisse_text = fields.Text(related="product_id.clisse_id.text")
    clisse_desing = fields.Binary(related="product_id.clisse_id.image_design")
    clisse_barcode = fields.Binary(related="product_id.clisse_id.image_barcode")
    clisse_description_label = fields.Text(related="product_id.clisse_id.description_label")
    clisse_state = fields.Selection(related="product_id.clisse_id.state")

    product_is_not_sticker = fields.Boolean(related="product_id.category_is_not_sticker")

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if bool(res.product_tmpl_id.clisse_id) and res.product_tmpl_id.bom_count > 1:
            raise UserError(
                "Este producto es un clisse y no puede tener mas de una lista de materiales.")
