
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class binaural_account_payment_register(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Herencia de wizard para registro de pagos'

    type_payment_id = fields.Many2one(comodel_name="tipopago.webpos", string="Tipo de pago", required=True)    

    def _create_payment_vals_from_wizard(self):

        self.ensure_one()
        res = super(binaural_account_payment_register, self)._create_payment_vals_from_wizard()        

        if self.type_payment_id:
            res['type_payment_id'] = self.type_payment_id.id

        return res
