import logging
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)


class ClisseSales(models.Model):
    """Clisse functionality related to Sales."""
    _inherit = "hagus.clisse"

    quantity = fields.Float(
        string="Cantidad a Producir (Por Millar)", digits=(14, 2), default=1, required=True)
    decrease = fields.Float(string="Merma", digits=(14, 2))

    rubber_base = fields.Float(
        string="Caucho base", digits=(14, 2), default=1.05)
    rubber_cost = fields.Float(string="Costo de Caucho", digits=(
        14, 2), compute="_compute_rubber_cost")
    negative_base = fields.Float(
        string="Negativo base", digits=(14, 2), default=.1)
    negative_cost = fields.Float(string="Costo del Negativo", digits=(
        14, 2), compute="_compute_negative_cost")
    negative_plus_rubber_cost = fields.Float(string="Costo Negativo / Caucho", digits=(
        14, 2), compute="_compute_negative_plus_rubber_cost")

    paper_cost = fields.Float(string="Costo de Papel", digits=(
        14, 2), compute="_compute_paper_cost")

    handm_cost = fields.Float(string="Costo H/M", digits=(14, 2))
    print_cost = fields.Float(string="Costo de Impresión", digits=(
        14, 2), compute="_compute_print_cost")

    coiling_cost = fields.Float(string="Costo de Embobinado", digits=(
        14, 2), compute="_compute_coiling_cost")

    profit = fields.Float(string="Ganancia", digits=(14, 2))

    packing_cost = fields.Float(string="Costo de Empaquetado", digits=(
        14, 2), compute="_compute_packing_cost")

    percentage = fields.Float(string="Porcentaje a Aplicar", digits=(3, 2))

    product_type = fields.Many2one(
        "product.category", string="Tipo de Producto",
        domain="[('name', 'in', ('Calcomanía', 'Calcomania', 'Etiqueta'))]",
        default=lambda self: self.env["product.category"].search(
            [("name", '=', "Calcomanía")]),
        required=True)
    product_template_ids = fields.One2many(
        "product.template", "clisse_id", string="Producto")

    thousand_cost = fields.Float(string="Precio por Millar", digits=(
        14, 2), compute="_compute_thousand_cost")
    sale_order_ids = fields.Many2many(
        "sale.order", string="Ordenes de Venta", readonly=True)

    crm_lead_id = fields.Many2one("crm.lead", string="Lead Asociado")

    @api.model
    def create(self, vals):
        coil = 0
        bushing = 0

        res = super().create(vals)

        # Creating a product based on the clisse information.
        res.product_template_ids = self.env["product.template"].create({
            "name": res.description,
            "price": res.thousand_cost,
            "categ_id": res.product_type.id,
            "description": res.description,
            "standard_price": res.paper_cost + res.print_cost + res.coiling_cost + res.negative_plus_rubber_cost + res.art_cost,
            "route_ids": [self.env["stock.location.route"].search([("name", '=', "Fabricar")]).id],
        })

        for material in res.materials_lines_id:
            # Check if a clisse has more than one material with the "Bobina" category.
            if bool(material.product_category_id) and \
               material.product_category_id.name.lower() == "bobina":
                coil += 1
            if coil > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de una bobina como material.")

            # Check if a clisse has more than one material with the "Buje" category.
            if bool(material.product_category_id) and \
               material.product_category_id.name.lower() == "buje":
                bushing += 1
                # Calculate the bushing quantity
                material.qty = res.quantity
            if bushing > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un buje como material.")

        lead_id = self.env.context.get("lead_id")
        if bool(lead_id):
            res.crm_lead_id = lead_id

        return res

    def write(self, vals):
        res = super().write(vals)
        self.product_template_ids.write({
            "price": self.thousand_cost,
            "description": self.description,
            "categ_id": self.product_type.id,
            "standard_price": self.paper_cost + self.print_cost + self.coiling_cost + self.negative_plus_rubber_cost + self.art_cost,
        })
        return res

    def action_create_sale_order(self):
        for clisse in self:
            last_order_quantity = clisse.sale_order_ids[0].order_line[0].product_uom_qty if bool(
                clisse.sale_order_ids) else None
            if not bool(clisse.partner_id):
                raise ValidationError(
                    "Antes de generar un presupuesto debe seleccionar al cliente.")
            if bool(last_order_quantity) and \
                    last_order_quantity == clisse.quantity:
                raise UserError(
                    "La misma orden de venta no puede ser generada dos veces.")
            sale_order = self.env["sale.order"].create({
                "partner_id": clisse.partner_id.id,
            })
            sale_order.write({
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "order_id": sale_order.id,
                            "name": clisse.product_template_ids[0].name,
                            "product_id": clisse.product_template_ids[0].product_variant_id.id,
                            "product_uom_qty": clisse.quantity,
                            "customer_lead": 7,
                        }
                    ),
                ]
            })

            clisse.sale_order_ids += sale_order
            if bool(clisse.crm_lead_id):
                clisse.crm_lead_id.order_ids += sale_order

        return {
            "type": "ir.actions.act_window",
            "name": "sale.order.form",
            "res_model": "sale.order",
            "res_id": sale_order.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "self",
        }

    @api.onchange("materials_lines_id")
    def _onchange_materials_lines_id(self):
        rubber = 0
        negative = 0
        coil = 0
        bushing = 0
        for material in self.materials_lines_id:
            # Check if a clisse has more than one material with the "Bobina" category.
            if bool(material.product_id.categ_id) and \
               material.product_category_id.name.lower() == "bobina":
                coil += 1
            if coil > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de una bobina como material.")

            # Check if a clisse has more than one material with the "Buje" category.
            if bool(material.product_id.categ_id) and \
               material.product_category_id.name.lower() == "buje":
                bushing += 1
                # Calculate the bushing quantity
                material.qty = self.quantity
            if bushing > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un buje como material.")

    @api.onchange("quantity")
    def onchange_quantity(self):
        for clisse in self:
            if clisse.quantity <= 0:
                raise ValidationError(
                    "La cantidad a producir debe ser un numero positivo mayor a cero.")

    @api.depends("width_inches", "length_inches", "materials_lines_id")
    def _compute_rubber_cost(self):
        self.rubber_cost = 0
        for clisse in self:
            total_colors = 0
            rubber_base = clisse.rubber_base
            for product in clisse.materials_lines_id:
                if bool(product.product_category_id) and \
                        product.product_category_id.name.lower() == "tinta":
                    if product.qty >= 1:
                        total_colors += product.qty
                    else:
                        total_colors += 1
            clisse.rubber_cost = clisse.width_inches * \
                clisse.length_inches * total_colors * rubber_base

    @api.depends("width_inches", "length_inches", "materials_lines_id")
    def _compute_negative_cost(self):
        self.negative_cost = 0
        for clisse in self:
            total_colors = 0
            negative_base = clisse.negative_base
            for product in clisse.materials_lines_id:
                if product.product_category_id.name.lower() == "tinta":
                    if product.qty >= 1:
                        total_colors += product.qty
                    else:
                        total_colors += 1
            clisse.negative_cost = clisse.width_inches * \
                clisse.length_inches * total_colors * negative_base

    @api.depends("negative_cost", "rubber_cost")
    def _compute_negative_plus_rubber_cost(self):
        self.negative_plus_rubber_cost = 0
        for clisse in self:
            clisse.negative_plus_rubber_cost = clisse.negative_cost + \
                clisse.rubber_cost

    @api.depends("width_inches", "length_inches", "materials_lines_id", "quantity", "decrease")
    def _compute_paper_cost(self):
        self.paper_cost = 0
        for clisse in self:
            material_cost = 0
            width = clisse.width_inches
            for material in clisse.materials_lines_id:
                if bool(material.product_category_id) and \
                   material.product_category_id.name.lower() == "bobina":
                    material_cost = material.cost
                    break
            clisse.paper_cost = (width * clisse.length_inches * material_cost * clisse.quantity) + \
                                (clisse.decrease * width / 1000 * material_cost)

    @api.depends("length_inches", "quantity", "materials_lines_id", "handm_cost")
    def _compute_print_cost(self):
        self.print_cost = 0
        for clisse in self:
            total_colors = 0
            for product in clisse.materials_lines_id:
                if bool(product.product_category_id) and \
                   product.product_category_id.name.lower() == "tinta":
                    if product.qty >= 1:
                        total_colors += product.qty
                    else:
                        total_colors += 1
            clisse.print_cost = ((clisse.length_inches * 25.4 * clisse.quantity / 13.33) + (
                total_colors * 10)) * clisse.handm_cost + (total_colors * 2.4)

    @api.depends("materials_lines_id", "quantity")
    def _compute_coiling_cost(self):
        self.coiling_cost = 0
        for clisse in self:
            cost = 0
            qty = 0
            for product in clisse.materials_lines_id:
                if bool(product.product_category_id) and \
                   product.product_category_id.name.lower() == "buje":
                    cost = product.cost
                    qty = product.qty
                    break
            clisse.coiling_cost = (cost * qty) + (qty * .1089)

    @api.depends("quantity")
    def _compute_packing_cost(self):
        self.packing_cost = 0
        for clisse in self:
            clisse.packing_cost = clisse.quantity * .1

    @api.depends("paper_cost", "print_cost", "coiling_cost", "packing_cost", "percentage", "profit", "quantity")
    def _compute_thousand_cost(self):
        self.thousand_cost = 0
        for clisse in self:
            if clisse.quantity > 0:
                total_cost = clisse.paper_cost + clisse.print_cost + \
                    clisse.coiling_cost + clisse.packing_cost
                total_price_without_profit = total_cost + \
                    (total_cost * (clisse.percentage / 100))
                clisse.thousand_cost = (total_price_without_profit + (
                    total_price_without_profit * (clisse.profit / 100))) / clisse.quantity

    @api.constrains("product_template_ids")
    def _check_product_template_ids(self):
        for clisse in self:
            if len(clisse.product_template_ids) > 1:
                raise ValidationError(
                    "El clisse no puede tener mas de un producto.")

    @api.constrains("quantity")
    def check_quantity(self):
        for clisse in self:
            if clisse.quantity <= 0:
                raise ValidationError(
                    "La cantidad debe ser un numero positivo mayor a cero.")


class HagusClisseLines(models.Model):
    _name = 'hagus.clisse.line'
    _rec_name = 'product_id'
    # ojo con product template
    product_id = fields.Many2one('product.product', string='Producto')
    description = fields.Char(string='Descripción')
    qty = fields.Float(string='Cantidad', digits=(16, 2), default=1)
    cost = fields.Float(string='Costo', digits=(
        16, 2), related="product_id.standard_price", readonly=False, store_true=True)
    clisse_id = fields.Many2one('hagus.clisse', string='Clisse asociado')
    product_category_id = fields.Many2one(
        string="Categoría", related="product_id.categ_id", readonly=False, store_true=True)
