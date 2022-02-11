from odoo import fields, models, api
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    clisse_code = fields.Char(related="product_id.clisse_id.code")
    clisse_date = fields.Date(related="product_id.clisse_id.date")
    clisse_partner = fields.Char(
        string="Cliente", related="product_id.clisse_id.partner_id.name", store=True)
    clisse_troquel = fields.Char(
        string="Troquel", related="product_id.clisse_id.troquel_id.code", store=True)
    clisse_width_inches = fields.Float(
        related="product_id.clisse_id.width_inches", store=True)
    clisse_length_inches = fields.Float(
        related="product_id.clisse_id.length_inches", store=True)
    clisse_lines_width = fields.Integer(
        related="product_id.clisse_id.troquel_line", store=True, readonly=False)
    clisse_labels_per_roll = fields.Float(
        related="product_id.clisse_id.labels_per_roll", store=True)
    clisse_size = fields.Char(related="product_id.clisse_id.size", store=True)
    clisse_background = fields.Char(
        related="product_id.clisse_id.background", store=True)
    clisse_orientation = fields.Char(
        string="Orientación", related="product_id.clisse_id.orientation_id.abbreviation", store=True)
    clisse_orientation_image = fields.Binary(
        related="product_id.clisse_id.orientation_image", store=True)
    clisse_finish_type = fields.Char(
        string="Acabado", related="product_id.clisse_id.finish_type_id.description", store=True)
    clisse_observations = fields.Text(
        related="product_id.clisse_id.observations", store=True)
    clisse_text = fields.Text(related="product_id.clisse_id.text", store=True)
    clisse_desing = fields.Binary(
        related="product_id.clisse_id.image_design", store=True)
    clisse_barcode = fields.Binary(
        related="product_id.clisse_id.image_barcode", store=True)
    clisse_description_label = fields.Text(
        related="product_id.clisse_id.description_label", store=True)
    clisse_state = fields.Selection(
        related="product_id.clisse_id.state", store=True)

    product_is_not_sticker = fields.Boolean(
        related="product_id.category_is_not_sticker", store=True)

    # Tab de Venta
    quantity = fields.Float(
        related="product_id.clisse_id.quantity", store=True)
    decrease = fields.Float(
        related="product_id.clisse_id.decrease", store=True)
    handm_cost = fields.Float(
        related="product_id.clisse_id.handm_cost", store=True)
    seller_id = fields.Many2one(
        related="product_id.clisse_id.seller_id", store=True)
    payment_method_id = fields.Many2one(
        related="product_id.clisse_id.payment_method_id", store=True)
    product_type = fields.Many2one(
        related="product_id.clisse_id.product_type", store=True)
    payment_term = fields.Many2one(
        related="product_id.clisse_id.payment_term", store=True)
    has_rubber = fields.Boolean(related="product_id.clisse_id.has_rubber")
    rubber_base = fields.Float(
        related="product_id.clisse_id.rubber_base", store=True)
    rubber_cost = fields.Float(string="Costo de Caucho", digits=(
        14, 2), compute="_compute_rubber_cost")
    negative_base = fields.Float(
        related="product_id.clisse_id.negative_base", store=True)
    negative_cost = fields.Float(string="Costo del Negativo", digits=(
        14, 2), compute="_compute_negative_cost")
    negative_plus_rubber_cost = fields.Float(string="Costo Negativo / Caucho", digits=(
        14, 2), compute="_compute_negative_plus_rubber_cost")
    paper_cost = fields.Float(string="Costo de Papel", digits=(
        14, 2), compute="_compute_paper_cost")
    print_cost = fields.Float(string="Costo de Impresión", digits=(
        14, 2), compute="_compute_print_cost")
    coiling_cost = fields.Float(string="Costo de Embobinado", digits=(
        14, 2), compute="_compute_coiling_cost")
    packing_cost = fields.Float(string="Costo de Empaquetado", digits=(
        14, 2), compute="_compute_packing_cost")
    has_art = fields.Boolean(
        related="product_id.clisse_id.has_art", store=True)
    art_cost = fields.Float(
        related="product_id.clisse_id.art_cost", store=True)
    profit = fields.Float(related="product_id.clisse_id.profit", store=True)
    percentage = fields.Float(
        related="product_id.clisse_id.percentage", store=True)
    total_cost = fields.Float(string="Costo Total", digits=(
        14, 2), compute="_compute_total_cost")
    expenses = fields.Float(string="Gastos Generales", digits=(
        14, 2), compute="_compute_expenses")
    subtotal = fields.Float(related="product_id.clisse_id.subtotal")
    total_price = fields.Float(
        related="product_id.clisse_id.total_price", store=True)
    thousand_price = fields.Float(
        related="product_id.clisse_id.thousand_price", store=True)

    # Tab de Producción
    paper_cut_inches = fields.Float(
        related="product_id.clisse_id.paper_cut_inches", store=True)
    paper_cut_centimeters = fields.Float(
        related="product_id.clisse_id.paper_cut_centimeters", store=True)
    troquel_line = fields.Integer(
        related="product_id.clisse_id.troquel_line", store=True)
    troquel_teeth = fields.Integer(
        related="product_id.clisse_id.troquel_teeth", store=True)
    troquel_cylinders = fields.Integer(
        related="product_id.clisse_id.troquel_cylinders", store=True)
    troquel_repetition = fields.Integer(
        related="product_id.clisse_id.troquel_repetition", store=True)
    designed = fields.Char(related="product_id.clisse_id.designed", store=True)
    cut_date = fields.Date(related="product_id.clisse_id.cut_date", store=True, readonly=False)
    coil_qty = fields.Integer(
        related="product_id.clisse_id.coil_qty", store=True, readonly=False)
    cutter = fields.Many2one(related="product_id.clisse_id.cutter", store=True, readonly=False)
    estimate_msi = fields.Float(
        related="product_id.clisse_id.estimate_msi", store=True, readonly=False)
    consumed_msi = fields.Float(
        related="product_id.clisse_id.consumed_msi", store=True, readonly=False)
    margin = fields.Float(
        related="product_id.clisse_id.margin", store=True, readonly=False)
    total_mts = fields.Float(related="product_id.clisse_id.total_mts")
    total_ft = fields.Float(related="product_id.clisse_id.total_ft")
    mts_settings = fields.Float(
        related="product_id.clisse_id.mts_settings", store=True, readonly=False)
    mts_print = fields.Float(
        related="product_id.clisse_id.mts_print", store=True, readonly=False)
    coil_id = fields.Many2one(
        related="product_id.clisse_id.coil_id", store=True, readonly=False)
    press_machine = fields.Char(
        related="product_id.clisse_id.press_machine", store=True, readonly=False)
    mount_start_date = fields.Date(
        related="product_id.clisse_id.mount_start_date", store=True, readonly=False)
    mount_start_time = fields.Float(
        related="product_id.clisse_id.mount_start_time", store=True, readonly=False)
    mount_end_date = fields.Date(
        related="product_id.clisse_id.mount_end_date", store=True, readonly=False)
    pressman_1 = fields.Many2one(
        related="product_id.clisse_id.pressman_1", store=True, readonly=False)
    turn_pressman_1 = fields.Char(
        related="product_id.clisse_id.turn_pressman_1", store=True, readonly=False)
    start_pressman_1 = fields.Float(
        related="product_id.clisse_id.start_pressman_1", store=True, readonly=False)
    end_pressman_1 = fields.Float(
        related="product_id.clisse_id.end_pressman_1", store=True, readonly=False)
    produced_meters_pressman_1 = fields.Float(
        related="product_id.clisse_id.produced_meters_pressman_1", store=True, readonly=False)
    pressman_2 = fields.Many2one(
        related="product_id.clisse_id.pressman_2", store=True, readonly=False)
    turn_pressman_2 = fields.Char(
        related="product_id.clisse_id.turn_pressman_2", store=True, readonly=False)
    start_pressman_2 = fields.Float(
        related="product_id.clisse_id.start_pressman_2", store=True, readonly=False)
    end_pressman_2 = fields.Float(
        related="product_id.clisse_id.end_pressman_2", store=True, readonly=False)
    produced_meters_pressman_2 = fields.Float(
        related="product_id.clisse_id.produced_meters_pressman_2", store=True, readonly=False)
    digits_number = fields.Float(
        related="product_id.clisse_id.digits_number", store=True)
    coiling_start_date = fields.Date(
        related="product_id.clisse_id.coiling_start_date", store=True, readonly=False)
    coiling_start_time = fields.Float(
        related="product_id.clisse_id.coiling_start_time", store=True, readonly=False)
    coiling_end_date = fields.Date(
        related="product_id.clisse_id.coiling_end_date", store=True, readonly=False)
    delivered_msi = fields.Float(
        related="product_id.clisse_id.delivered_msi", store=True, readonly=False)
    msi_to_return = fields.Float(
        related="product_id.clisse_id.msi_to_return", store=True, readonly=False)
    coiler = fields.Many2one(related="product_id.clisse_id.coiler", store=True, readonly=False)
    turn_coiler = fields.Char(
        related="product_id.clisse_id.turn_coiler", store=True, readonly=False)
    t_roll = fields.Char(related="product_id.clisse_id.t_roll", store=True, readonly=False)
    coiling_problems = fields.Text(
        related="product_id.clisse_id.coiling_problems", store=True, readonly=False)

    coil_cost = fields.Float(string="Costo de Bobina", digits=(
        14, 2), compute="_compute_coil_cost")

    def write(self, vals):
        res = super().write(vals)
        # Agregando la orden de produccion a la lista de ordenes de produccion
        # del clisse cuyo producto forma parte de la misma.
        self.product_id.clisse_id.mrp_production_ids += self.env["mrp.production"].search([
                                                                                          ("id", '=', self.id)])
        return res

    # Metodos del Tab de Venta
    @api.depends("clisse_width_inches", "clisse_length_inches", "move_raw_ids")
    def _compute_rubber_cost(self):
        self.rubber_cost = 0
        for order in self:
            total_colors = 0
            rubber_base = order.rubber_base
            for product in order.move_raw_ids:
                category = product.product_id.categ_id if bool(
                    product.product_id.categ_id) else None
                if bool(category) and category.name.lower() == "tinta":
                    if product.product_uom_qty >= 1:
                        total_colors += product.product_uom_qty
                    else:
                        total_colors += 1
            order.rubber_cost = order.clisse_width_inches * \
                order.clisse_length_inches * total_colors * rubber_base

    @api.depends("clisse_width_inches", "clisse_length_inches", "move_raw_ids")
    def _compute_negative_cost(self):
        self.negative_cost = 0
        for order in self:
            total_colors = 0
            negative_base = order.negative_base
            for product in order.move_raw_ids:
                category = product.product_id.categ_id if bool(
                    product.product_id.categ_id) else None
                if bool(category) and category.name.lower() == "tinta":
                    if product.product_uom_qty >= 1:
                        total_colors += product.product_uom_qty
                    else:
                        total_colors += 1
            order.negative_cost = order.clisse_width_inches * \
                order.clisse_length_inches * total_colors * negative_base

    @api.depends("negative_cost", "rubber_cost")
    def _compute_negative_plus_rubber_cost(self):
        self.negative_plus_rubber_cost = 0
        for order in self:
            order.negative_plus_rubber_cost = order.negative_cost + \
                order.rubber_cost

    @api.depends("clisse_width_inches", "clisse_length_inches", "move_raw_ids", "quantity", "decrease")
    def _compute_paper_cost(self):
        self.paper_cost = 0
        for order in self:
            decrease = order.decrease if order.decrease > 0 else 1
            width = order.clisse_width_inches if order.clisse_width_inches > 0 else 1
            length = order.clisse_length_inches if order.clisse_length_inches > 0 else 1
            material_cost = 1
            for material in order.move_raw_ids:
                category = material.product_id.categ_id if bool(
                    material.product_id.categ_id) else None
                if bool(category) and \
                   category.name.lower() == "bobina":
                    material_cost = material.product_id.standard_price
                    break
            order.paper_cost = (width * length * material_cost * order.quantity) + \
                (decrease * width / 1000 * material_cost)

    @api.depends("clisse_length_inches", "quantity", "move_raw_ids", "handm_cost")
    def _compute_print_cost(self):
        self.print_cost = 0
        for order in self:
            length = order.clisse_length_inches if order.clisse_length_inches > 0 else 1
            total_colors = 0
            for product in order.move_raw_ids:
                category = product.product_id.categ_id if bool(
                    product.product_id.categ_id) else None
                if bool(category) and \
                   category.name.lower() == "tinta":
                    if product.product_uom_qty >= 1:
                        total_colors += product.product_uom_qty
                    else:
                        total_colors += 1
            order.print_cost = ((length * 25.4 * order.quantity / 13.33) + (
                total_colors * 10)) * order.handm_cost + (total_colors * 2.4)

    @api.depends("move_raw_ids", "quantity")
    def _compute_coiling_cost(self):
        self.coiling_cost = 0
        for order in self:
            cost = 1
            qty = order.quantity if order.quantity > 0 else 1
            for product in order.move_raw_ids:
                category = product.product_id.categ_id if bool(
                    product.product_id.categ_id) else None
                if bool(category) and \
                        category.name.lower() == "buje":
                    cost = product.product_id.standard_price
                    break
            order.coiling_cost = (cost * qty) + (qty * .1089)

    @api.depends("quantity")
    def _compute_packing_cost(self):
        self.packing_cost = 0
        for order in self:
            order.packing_cost = order.quantity * .1

    @api.depends("paper_cost", "print_cost", "coiling_cost", "packing_cost", "negative_plus_rubber_cost", "art_cost")
    def _compute_total_cost(self):
        self.total_cost = 0
        for order in self:
            order.total_cost = order.paper_cost + order.print_cost + \
                order.coiling_cost + order.packing_cost
            if order.has_rubber:
                order.total_cost += order.negative_plus_rubber_cost
            if order.has_art:
                order.total_cost += clisse.art_cost

    @api.depends("total_cost", "percentage")
    def _compute_expenses(self):
        self.expenses = 0
        for order in self:
            order.expenses = order.total_cost * (order.percentage / 100)

    # Metodos del tab de Producción
    @api.depends("coil_cost")
    def _compute_coil_cost(self):
        self.coil_cost = 0
        for order in self:
            if order.product_is_not_sticker:
                continue
            for line in order.move_raw_ids:
                if line.product_id.categ_id.name.lower() == "bobina":
                    coil_standard_price = line.product_id.standard_price
                    coil_qty = line.product_uom_qty
                    break
            order.coil_cost = coil_standard_price * coil_qty


class StockMove(models.Model):
    _inherit = "stock.move"

    lot_id = fields.Many2one(
        "stock.production.lot", string="Lote", readonly=True, compute="_compute_lot_id")

    @api.depends("lot_id")
    def _compute_lot_id(self):
        self.lot_id = False
        for move in self:
            if bool(move.move_line_ids):
                move.lot_id = move.move_line_ids[0].lot_id


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if bool(res.product_tmpl_id.clisse_id) and res.product_tmpl_id.bom_count > 1:
            raise UserError(
                "Este producto es un clisse y no puede tener mas de una lista de materiales.")
        return res


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    bom_id = fields.Many2one(
        'mrp.bom', 'Parent BoM',
        index=True, ondelete='cascade', required=False)
