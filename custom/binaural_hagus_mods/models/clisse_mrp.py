import logging
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class ClisseMrp(models.Model):
    """Clisse functionality related to mrp."""
    _inherit = "hagus.clisse"

    cut_width = fields.Float(string="Ancho de Corte", digtis=(14, 6))
    troquel_line = fields.Integer(
        string="Linea Troquel", related="troquel_id.lines_width")
    troquel_teeth = fields.Integer(
        string="Dientes del Troquel", related="troquel_id.lines_width")
    troquel_cylinders = fields.Integer(
        string="Cilindros", related="troquel_id.cylinders")
    troquel_repetition = fields.Integer(
        string="Repetición", related="troquel_id.repetition")
    paper_cut_inches = fields.Float(
        string="Corte de Papel (pulgadas)", digits=(14, 6))
    # Campo designed to ??
    mrp_production_ids = fields.Many2many(
        "mrp.production", string="Orden de Producción")
    cut_date = fields.Date(string="Fecha de Corte",
                           default=lambda self: fields.Date.today())
    coil_qty = fields.Integer(string="Cantidad de Bobinas")
    cutter = fields.Many2one("hr.employee", string="Cortador")
    coil = fields.Many2one("product.template", string="Bobina")
    scrap = fields.Float(string="Retazo", digits=(14, 6))
    estimate_msi = fields.Float(string="MSI Estimados", digits=(14, 6))
    consumed_msi = fields.Float(string="MSI Consumidos", digits=(14, 6))
    margin = fields.Float(string="Margen", digits=(14, 6))
    total_mts = fields.Float(string="Total Metros", digits=(14, 6))
    net_mts = fields.Float(string="Metros Netos", digits=(14, 6))
    mts_settings = fields.Float(string="Ajustes Metros", digits=(14, 6))
    mts_print = fields.Float(string="Tiro de metros", digits=(14, 6))
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
        string="Metros producidos prensista 1", digits=(14, 6))
    pressman_2 = fields.Many2one("hr.employee", string="Prensista 2")
    turn_pressman_2 = fields.Char(string="Turno prensista 2")
    start_pressman_2 = fields.Float(
        string="Inicio prensista 2", digits=(14, 2), copy=False)
    end_pressman_2 = fields.Float(
        string="Terminación prensista 2", digits=(14, 2), copy=False)
    produced_meters_pressman_2 = fields.Float(
        string="Metros producidos prensista 2", digits=(14, 6))
    digits_number = fields.Float(string="Nro de dígitos", digits=(14, 6))
    coiling_start_date = fields.Date(string="Fecha de Inicio",
                                     default=lambda self: fields.Date.today())
    coiling_start_time = fields.Float(
        string="Hora de Inicio", digits=(12, 2), copy=False)
    coiling_end_date = fields.Date(string="Fecha de Terminación",
                                   default=lambda self: fields.Date.today())
    delivered_msi = fields.Float(string="MSI Entregados", digits=(14, 6))
    msi_to_return = fields.Float(string="MSI por Devolver", digits=(14, 6))
    coiler = fields.Many2one("hr.employee", string="Embobinado por")
    turn_coiler = fields.Char(string="Turno embobinador")
    t_roll = fields.Char(string="Rollo T")
    surplus_roll = fields.Float(string="Sobrante Rollo", digits=(14, 6))
    coiling_problems = fields.Text(string="Problemas de Embobinado")

    def action_create_mrp_production(self):
        pass
