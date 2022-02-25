from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    clisse_ids = fields.One2many("hagus.clisse", "crm_lead_id", string="Clisse Asociados")

    def action_create_clisse(self):
        return {
            "type": "ir.actions.act_window",
            "name": "hagus.clisse.form",
            "res_model": "hagus.clisse",
            "view_type": "form",
            "view_mode": "form",
            "target": "self",
            "context": {
                "lead_id": self.id,
                "default_partner_id": self.partner_id.id,
            },
        }
