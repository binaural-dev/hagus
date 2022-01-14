from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    company_dv = fields.Integer(string="DV")

    # @api.constrains("company_dv")
    # def _check_company_dv(self):
        # for company in self:
            # number = company.company_dv
            # if number and len(str(abs(number))) > 1:
                # raise ValidationError("El DV deber ser un único dígito.")

