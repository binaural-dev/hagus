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

    product_type = fields.Many2one(
        "product.category", string="Tipo de Producto",
        domain="[('name', 'in', ('Calcomanía', 'Calcomania', 'Etiqueta'))]",
        default=lambda self: self.env["product.category"].search(
            [("name", '=', "Calcomanía")]),
        required=True)
    product_template_ids = fields.One2many(
        "product.template", "clisse_id", string="Producto")
    seller_id = fields.Many2one(
        'res.partner', string='Vendedor', domain="[('active', '=', True)]")

    has_rubber = fields.Boolean(string="Tiene Caucho", default=True)
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

    packing_cost = fields.Float(string="Costo de Empaquetado", digits=(
        14, 2), compute="_compute_packing_cost")
    has_art = fields.Boolean(string="Tiene Arte", default=False)
    art_cost = fields.Float(string="Costo de Arte", digits=(14, 2))

    profit = fields.Float(string="Ganancia", digits=(14, 2))

    percentage = fields.Float(string="Porcentaje de Gasto", digits=(3, 2))

    total_cost = fields.Float(string="Costo Total", digits=(
        14, 2), compute="_compute_total_cost")
    expenses = fields.Float(string="Gastos Generales", digits=(
        14, 2), compute="_compute_expenses")
    subtotal = fields.Float(string="Subtotal", digits=(
        14, 2), compute="_compute_subtotal")
    total_price = fields.Float(string="Precio Total", digits=(
        14, 2), compute="_compute_total_price")
    thousand_price = fields.Float(string="Precio por Millar", digits=(
        14, 2), compute="_compute_thousand_price")
    sale_order_ids = fields.Many2many(
        "sale.order", string="Ordenes de Venta", readonly=True)

    crm_lead_id = fields.Many2one("crm.lead", string="Lead Asociado")

    @api.model
    def create(self, vals):
        coil = 0
        bushing = 0
        product_uom = self.env["uom.uom"].search([("name", '=', "Millar")])

        res = super().create(vals)

        if not bool(product_uom):
            raise UserError(
                "No existe la unidad de medida 'millar', debe crearla antes de poder crear un clisse.")

        # Creando un producto basado en la informacion del clisse.
        route = self.env["stock.location.route"].search(
            [("name", '=', "Fabricar")]).id
        res.product_template_ids = self.env["product.template"].create({
            "name": res.description,
            "price": res.thousand_price,
            "categ_id": res.product_type.id,
            "description": res.description,
            "uom_id": product_uom.id,
            "uom_po_id": product_uom.id,
            "sale_ok": True,
            "purchase_ok": False,
            "type": "product",
            "standard_price": self.total_cost,
            "list_price": self.thousand_price,
            "route_ids": [route] if bool(route) else [1],
            "image_1920": res.image_design,
            "invoice_policy": "order",
        })
        # Creando la lista de materiales del producto.
        mrp_bom = self.env["mrp.bom"].create({
            "product_tmpl_id": res.product_template_ids.id,
            "product_qty": res.quantity,
            "code": res.code,
        })

        mrp_bom.write({
            "operation_ids": [
                (
                    0,
                    4,
                    {
                        "name": "Cortar bobina",
                        "bom_id": mrp_bom.id,
                        "workcenter_id": self.env["mrp.workcenter"].search([("name", '=', "Corte")]).id,
                        "time_mode": "manual",
                    }
                ),
                (
                    0,
                    4,
                    {
                        "name": f"Impresión {res.product_template_ids.name}",
                        "bom_id": mrp_bom.id,
                        "workcenter_id": self.env["mrp.workcenter"].search([("name", '=', "Prensa 1")]).id,
                        "time_mode": "manual",
                    }
                ),
                (
                    0,
                    4,
                    {
                        "name": f"Embobinado {res.product_template_ids.name}",
                        "bom_id": mrp_bom.id,
                        "workcenter_id": self.env["mrp.workcenter"].search([("name", '=', "Embobinado")]).id,
                        "time_mode": "manual",
                    }
                ),
                (
                    0,
                    4,
                    {
                        "name": f"Calidad",
                        "bom_id": mrp_bom.id,
                        "workcenter_id": self.env["mrp.workcenter"].search([("name", '=', "Control de Calidad")]).id,
                        "time_mode": "manual",
                    }
                ),
            ]
        })
        
        for material in res.materials_lines_id:
            # Comprobar que un clisse no pueda tener mas de un material con la categoria "Bobina".
            if bool(material.product_category_id) and \
               material.product_category_id.name.lower() == "bobina":
                coil += 1
            if coil > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de una bobina como material.")

            # Comprobar que un clisse no pueda tener mas de un material con la categoria "Buje".
            if bool(material.product_category_id) and \
               material.product_category_id.name.lower() == "buje":
                bushing += 1
                # Calculate the bushing quantity
                material.qty = res.quantity
            if bushing > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un buje como material.")

            # Creando una linea de la lista de materiales del producto.
            mrp_bom.bom_line_ids += self.env["mrp.bom.line"].create({
                "bom_id": mrp_bom.id,
                "product_id": material.product_id.id,
                "product_qty": material.qty,
            })

        lead_id = self.env.context.get("lead_id")
        if bool(lead_id):
            res.crm_lead_id = lead_id

        return res

    def write(self, vals):
        res = super().write(vals)
        # Actualizando el producto.
        self.product_template_ids[0].write({
            "image_1920": self.image_design,
        })
        self.product_template_ids.write({
            "price": self.thousand_price,
            "description": self.description,
            "categ_id": self.product_type.id,
            "standard_price": self.total_cost,
            "list_price": self.thousand_price,
        })
        # Actualizando la lista de materiales del producto.
        bom_id = self.env["mrp.bom"].search([("id", '=', self.product_template_ids.bom_ids.id)])

        for line in self.product_template_ids.bom_ids.bom_line_ids:
            self.product_template_ids.bom_ids.write({
                "bom_line_ids": [(5, line.id)],
            })
        for material in self.materials_lines_id:
            bom_line = self.env["mrp.bom.line"].create({
                "bom_id": bom_id.id,
                "product_id": material.product_id.id,
                "product_qty": material.qty,
                "product_uom_id": material.product_id.uom_id.id,
            })
            self.product_template_ids.bom_ids.bom_line_ids += bom_line
        return res

    def action_create_sale_order(self):
        for clisse in self:
            last_order_quantity = clisse.sale_order_ids[0].order_line[0].product_uom_qty if bool(
                clisse.sale_order_ids) else None
            if not bool(clisse.partner_id):
                raise ValidationError(
                    "Antes de generar un presupuesto debe seleccionar al cliente.")
            if bool(clisse.sale_order_ids) and clisse.sale_order_ids[0].state != "sale" \
                    and clisse.sale_order_ids[0].state != "cancel":
                raise ValidationError(
                    "No se puede generar una orden de venta " +
                    "si existe una orden anterior sin confirmar.")
            coil_exists = False
            bush_exists = False
            ink_exists = False
            for material in clisse.materials_lines_id:
                if bool(material.product_category_id) and\
                        material.product_category_id.name.lower() == "buje":
                    bush_exists = True
                if bool(material.product_category_id) and\
                        material.product_category_id.name.lower() == "bobina":
                    coil_exists = True
                if bool(material.product_category_id) and\
                        material.product_category_id.name.lower() == "tinta":
                    ink_exists = True
            if not coil_exists:
                raise UserError(
                    "Antes de generar una orden de venta debe agregar un producto de tipo " +
                    "\"Bobina\" en la lista de materiales.")
            if not bush_exists:
                raise UserError(
                    "Antes de generar una orden de venta debe agregar un producto de tipo " +
                    "\"Buje\" en la lista de materiales.")
            if not ink_exists:
                raise UserError(
                    "Antes de generar una orden de venta debe agregar al menos " +
                    "un producto de tipo \"Tinta\" en la lista de materiales.")

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
                            "price_unit": clisse.thousand_price,
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

    @api.onchange("materials_lines_id", "total_ft", "quantity")
    def _onchange_materials_lines_id(self):
        coil = 0
        bushing = 0
        labels_per_roll = self.labels_per_roll if self.labels_per_roll > 0 else 1
        for material in self.materials_lines_id:
            # Comprobar si un clisse tiene mas de un material con la categoria "Bobina"
            if bool(material.product_id.categ_id) and \
               material.product_category_id.name.lower() == "bobina":
                coil += 1
                # Calcular la cantidad y el costo de Bobina
                material.qty = self.total_ft
                material.cost = material.product_id.standard_price * material.qty
            if coil > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de una bobina como material.")

            # Comprobar si un clisse tiene mas de un material con la categoria "Buje"
            if bool(material.product_id.categ_id) and \
               material.product_category_id.name.lower() == "buje":
                bushing += 1
                # Calcular la cantidad de Buje
                material.qty = self.quantity * 1000 / labels_per_roll
                material.cost = material.product_id.standard_price * material.qty
            if bushing > 1:
                raise ValidationError(
                    "Un clisse no puede tener más de un buje como material.")

    @api.onchange("quantity")
    def _onchange_quantity(self):
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
                if bool(product.product_category_id) and product.product_category_id.name.lower() == "tinta":
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
            decrease = clisse.decrease if clisse.decrease > 0 else 1
            width = clisse.width_inches if clisse.width_inches > 0 else 1
            length = clisse.length_inches if clisse.length_inches > 0 else 1
            material_cost = 1
            for material in clisse.materials_lines_id:
                if bool(material.product_category_id) and \
                   material.product_category_id.name.lower() == "bobina":
                    material_cost = material.product_id.standard_price
                    break
            clisse.paper_cost = (width * length * material_cost * clisse.quantity) + \
                                (decrease * width / 1000 * material_cost)

    @api.depends("length_inches", "quantity", "materials_lines_id", "handm_cost")
    def _compute_print_cost(self):
        self.print_cost = 0
        for clisse in self:
            length = clisse.length_inches if clisse.length_inches > 0 else 1
            total_colors = 0
            for product in clisse.materials_lines_id:
                if bool(product.product_category_id) and \
                   product.product_category_id.name.lower() == "tinta":
                    if product.qty >= 1:
                        total_colors += product.qty
                    else:
                        total_colors += 1
            clisse.print_cost = ((length * 25.4 * clisse.quantity / 13.33) + (
                total_colors * 10)) * clisse.handm_cost + (total_colors * 2.4)

    @api.depends("materials_lines_id", "quantity")
    def _compute_coiling_cost(self):
        self.coiling_cost = 0
        for clisse in self:
            cost = 1
            qty = clisse.quantity if clisse.quantity > 0 else 1
            for product in clisse.materials_lines_id:
                if bool(product.product_category_id) and \
                        product.product_category_id.name.lower() == "buje":
                    cost = product.product_id.standard_price
                    break
            clisse.coiling_cost = (cost * qty) + (qty * .1089)

    @api.depends("quantity")
    def _compute_packing_cost(self):
        self.packing_cost = 0
        for clisse in self:
            clisse.packing_cost = clisse.quantity * .1

    @api.depends("paper_cost", "print_cost", "coiling_cost", "packing_cost", "negative_plus_rubber_cost", "art_cost")
    def _compute_total_cost(self):
        self.total_cost = 0
        for clisse in self:
            clisse.total_cost = clisse.paper_cost + clisse.print_cost + \
                clisse.coiling_cost + clisse.packing_cost
            if clisse.has_rubber:
                clisse.total_cost += clisse.negative_plus_rubber_cost
            if clisse.has_art:
                clisse.total_cost += clisse.art_cost

    @api.depends("total_cost", "percentage")
    def _compute_expenses(self):
        self.expenses = 0
        for clisse in self:
            clisse.expenses = clisse.total_cost * (clisse.percentage / 100)

    @api.depends("total_cost", "expenses")
    def _compute_subtotal(self):
        self.subtotal = 0
        for clisse in self:
            if clisse.quantity > 0:
                clisse.subtotal = clisse.total_cost + clisse.expenses

    @api.depends("subtotal", "profit")
    def _compute_total_price(self):
        self.total_price = 0
        for clisse in self:
            clisse.total_price = clisse.subtotal + \
                (clisse.subtotal * (clisse.profit / 100))

    @api.depends("total_price")
    def _compute_thousand_price(self):
        self.thousand_price = 0
        for clisse in self:
            clisse.thousand_price = clisse.total_price / clisse.quantity

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
    description = fields.Char(string='Descripción', related="product_id.name")
    qty = fields.Float(string='Cantidad', digits=(16, 2), default=1)
    cost = fields.Float(string='Costo', digits=(16, 2))
    clisse_id = fields.Many2one('hagus.clisse', string='Clisse asociado')
    product_category_id = fields.Many2one(
        string="Categoría", related="product_id.categ_id", readonly=False, store_true=True)
    product_uom_id = fields.Many2one(
        string="Unidad", related="product_id.product_tmpl_id.uom_id")
