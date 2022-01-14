from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_dv = fields.Integer(string="DV")

    # @api.constrains("partner_dv")
    # def _check_company_dv(self):
        # for partner in self:
            # number = partner.partner_dv
            # if number and len(str(abs(number))) > 1:
                # raise ValidationError("El DV deber ser un único dígito.")

