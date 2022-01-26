import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


class ClisseMrp(models.Model):
    """Clisse functionality related to mrp."""
    _inherit = "hagus.clisse"

    troquel_line = fields.Integer(
        string="Linea Troquel", related="troquel_id.lines_width")
    troquel_teeth = fields.Integer(
        string="Dientes del Troquel", related="troquel_id.teeth")
    troquel_cylinders = fields.Integer(
        string="Cilindros", related="troquel_id.cylinders")
    troquel_repetition = fields.Integer(
        string="Repetición", related="troquel_id.repetition")
    paper_cut_inches = fields.Float(
        string="Corte de Papel (pulgadas)", related="troquel_id.paper_cut_inches")
    paper_cut_centimeters = fields.Float(string="Corte de papel(centimetros)", digtis=(
        14, 2), related="troquel_id.paper_cut_centimeters")
    designed = fields.Char(string="Diseñado por",
                           related="troquel_id.designed")
    mrp_production_ids = fields.Many2many(
        "mrp.production", string="Orden de Producción")
    cut_date = fields.Date(string="Fecha de Corte",
                           default=lambda self: fields.Date.today())
    coil_qty = fields.Integer(string="Cantidad de Bobinas")
    cutter = fields.Many2one("hr.employee", string="Cortador")
    estimate_msi = fields.Float(string="MSI Estimados", digits=(
        14, 2), compute="_compute_estimate_msi")
    consumed_msi = fields.Float(string="MSI Consumidos", digits=(14, 2))
    margin = fields.Float(string="Margen", digits=(14, 2))
    total_mts = fields.Float(string="Total Metros", digits=(
        14, 2), compute="_compute_total_mts")
    net_mts = fields.Float(string="Metros Netos", digits=(14, 2))
    mts_settings = fields.Float(string="Ajustes Metros", digits=(14, 2))
    mts_print = fields.Float(string="Tiro de metros", digits=(14, 2))
    press_machine = fields.Char(string="Maquina Prensa")
    mount_start_date = fields.Date(string="Fecha de Inicio",
                                   default=lambda self: fields.Date.today())
    mount_start_time = fields.Float(
        string="Hora de Inicio", digits=(12, 2), copy=False)
    mount_end_date = fields.Date(string="Fecha de Terminación",
                                 default=lambda self: fields.Date.today())
    pressman_1 = fields.Many2one("hr.employee", string="Prensista 1")
    turn_pressman_1 = fields.Char(string="Turno prensista 1")
    start_pressman_1 = fields.Float(
        string="Inicio prensista 1", digits=(14, 2), copy=False)
    end_pressman_1 = fields.Float(
        string="Terminación prensista 1", digits=(14, 2), copy=False)
    produced_meters_pressman_1 = fields.Float(
        string="Metros producidos prensista 1", digits=(14, 2))
    pressman_2 = fields.Many2one("hr.employee", string="Prensista 2")
    turn_pressman_2 = fields.Char(string="Turno prensista 2")
    start_pressman_2 = fields.Float(
        string="Inicio prensista 2", digits=(14, 2), copy=False)
    end_pressman_2 = fields.Float(
        string="Terminación prensista 2", digits=(14, 2), copy=False)
    produced_meters_pressman_2 = fields.Float(
        string="Metros producidos prensista 2", digits=(14, 2))
    digits_number = fields.Float(string="Nro de dígitos", digits=(
        14, 2), compute="_compute_digits_number")
    coiling_start_date = fields.Date(string="Fecha de Inicio",
                                     default=lambda self: fields.Date.today())
    coiling_start_time = fields.Float(
        string="Hora de Inicio", digits=(12, 2), copy=False)
    coiling_end_date = fields.Date(string="Fecha de Terminación",
                                   default=lambda self: fields.Date.today())
    delivered_msi = fields.Float(string="MSI Entregados", digits=(14, 2))
    msi_to_return = fields.Float(string="MSI por Devolver", digits=(14, 2))
    coiler = fields.Many2one("hr.employee", string="Embobinado por")
    turn_coiler = fields.Char(string="Turno embobinador")
    t_roll = fields.Char(string="Rollo T")
    surplus_roll = fields.Float(string="Sobrante Rollo", digits=(14, 2))
    coiling_problems = fields.Text(string="Problemas de Embobinado")

    def action_create_mrp_production(self):
        for clisse in self:
            if not bool(clisse.sale_order_ids):
                raise ValidationError(
                    "No puede generar una orden de producción si no existe antes una orden de venta.")
            if bool(clisse.sale_order_ids) and clisse.sale_order_ids[0].state != "sale":
                raise ValidationError(
                    "No se puede generar una orden de producción " +
                    "sino se ha aprobado la orden de venta.")

            product = clisse.product_template_ids[0].product_variant_id
            mrp_production = self.env["mrp.production"].create({
                "product_id": product.id,
                "product_qty": clisse.quantity,
                "product_uom_id": product.uom_id.id,
                "consumption": "strict",
            })
            mrp_production.write({
                "bom_id": clisse.mrp_bom_id.id,
            })
            for material in clisse.materials_lines_id:
                mrp_production.move_raw_ids += self.env["stock.move"].create({
                    "product_id": material.product_id.id,
                    "name": material.description,
                    "product_uom": material.product_id.uom_id.id,
                    "company_id": self.env.company.id,
                    "product_uom_qty": material.qty,
                    "location_id": 1,
                    "location_dest_id": 1,
                    "procure_method": "make_to_stock",
                })
            clisse.mrp_production_ids += mrp_production
        return {
            "type": "ir.actions.act_window",
            "name": "mrp.production.form",
            "res_model": "mrp.production",
            "res_id": mrp_production.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "self",
        }

    @api.depends("troquel_id", "troquel_teeth", "troquel_repetition", "quantity")
    def _compute_total_mts(self):
        self.total_mts = 0
        for clisse in self:
            if bool(clisse.troquel_repetition) and clisse.troquel_repetition > 0 and \
                    bool(clisse.troquel_teeth) and bool(clisse.troquel_repetition) and \
                    bool(clisse.quantity):
                teeth_per_inch = clisse.troquel_teeth / 8
                clisse.total_mts = (
                    teeth_per_inch / clisse.troquel_repetition) * 25.4 * clisse.quantity

    @api.depends("paper_cut_inches", "total_mts")
    def _compute_estimate_msi(self):
        self.estimate_msi = 0
        for clisse in self:
            if clisse.paper_cut_inches > 0 and clisse.total_mts > 0:
                lineal_feet = clisse.total_mts * 3.28125
                clisse.estimate_msi = clisse.paper_cut_inches * lineal_feet * 0.012

    @api.depends("troquel_id", "troquel_teeth", "troquel_repetition", "labels_per_roll")
    def _compute_digits_number(self):
        self.digits_number = 0
        for clisse in self:
            if clisse.troquel_repetition > 0:
                teeth_per_inch = clisse.troquel_teeth / 8
                clisse.digits_number = ((teeth_per_inch / clisse.troquel_repetition) *
                                        clisse.labels_per_roll) / 10

    @api.onchange("mount_start_time", "start_pressman_1", "end_pressman_1", "start_pressman_2", "end_pressman_2")
    def _onchange_time(self):
        if self.mount_start_time < 0 or self.start_pressman_1 < 0 or \
                self.end_pressman_1 < 0 or self.start_pressman_2 < 0 or \
                self.end_pressman_2 < 0:
            raise ValidationError("La hora no puede ser menor a 0.")

        if self.mount_start_time > 24 or self.start_pressman_1 > 24 or \
                self.end_pressman_1 > 24 or self.start_pressman_2 > 24 or \
                self.end_pressman_2 > 24:
            raise ValidationError(
                "La hora no puede ser mayor a 24.")
