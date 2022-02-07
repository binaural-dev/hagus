import logging
from odoo.tests.common import Form, SavepointCase
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import float_compare
_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class HagusClisseTestCase(SavepointCase):

    @classmethod
    def setUpClass(self):
        super(HagusClisseTestCase, self).setUpClass()

        self.products = [
            self.env["product.product"].create({
                "name": "Tinta Negra",
                "categ_id": self.env["product.category"].search([("name", '=', "Tinta")]).id,
            }),
            self.env["product.product"].create({
                "name": "Tinta Azul",
                "categ_id": self.env["product.category"].search([("name", '=', "Tinta")]).id,
            }),
            self.env["product.product"].create({
                "name": "Bushing Test",
                "categ_id": self.env["product.category"].search([("name", '=', "Buje")]).id,
                "price": .085,
                "standard_price": .085,
            }),
            self.env["product.product"].create({
                "name": "Coil Test",
                "categ_id": self.env["product.category"].search([("name", '=', "Bobina")]).id,
                "price": .37,
                "standard_price": .37,
            }),
            self.env["product.product"].create({
                "name": "Coil Test 2",
                "categ_id": self.env["product.category"].search([("name", '=', "Bobina")]).id,
                "price": 1,
                "standard_price": 1,
            }),
            self.env["product.product"].create({
                "name": "Bushing Test 2",
                "categ_id": self.env["product.category"].search([("name", '=', "Buje")]).id,
                "price": 1,
                "standard_price": 1,
            }),
        ]

        self.troquels = [
            self.env["hagus.troquel"].create({
                "code": "troqtest1",
                "width_inches": 10,
                "paper_cut_inches": 25,
                "length_inches": 10,
                "teeth": 12,
                "repetition": 3,
            }),
        ]

        self.clisse = self.env["hagus.clisse"].create({
            "description": "cli012345",
            "troquel_id": self.troquels[0].id,
            "labels_per_roll": 10,
            "quantity": 15,
            "decrease": 2952.75,
            "handm_cost": .2312,
            "thousand_price": 500,
            "has_rubber": True,
            "percentage": 25,
            "profit": 100,
            "materials_lines_id": [
                (
                    0,
                    4,
                    {
                        "product_id": self.products[0].id,
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": self.products[1].id,
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": self.products[2].id,
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": self.products[3].id,
                    }
                ),
            ]
        })

    def test_add_more_than_one_product_with_coil_category_to_clisse(self):
        """
        Probar que no se puede agregar mas de un producto con
        la categoria 'bobina' a la lista de materiales de un clisse.
        """
        # Agregar mas de una bobina desde la creacion del clisse.
        with self.assertRaises(ValidationError):
            self.env["hagus.clisse"].create({
                "description": "cl01234",
                "troquel_id": self.troquels[0].id,
                "labels_per_roll": 10,
                "quantity": 15,
                "decrease": 2952.75,
                "handm_cost": .2312,
                "materials_lines_id": [
                    (
                        0,
                        4,
                        {
                            "product_id": self.products[2].id,
                            "cost": .085,
                        }
                    ),
                    (
                        0,
                        4,
                        {
                            "product_id": self.products[3].id,
                            "cost": .37
                        }
                    ),
                    (
                        0,
                        4,
                        {
                            "product_id": self.products[4].id,
                            "cost": 1
                        }
                    ),
                ]
            })
        # Agregar una bobina a un clisse que ya tiene una.
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                with f.materials_lines_id.new() as line:
                    line.product_id = self.products[4]

    def test_add_more_than_one_product_with_bushing_category_to_clisse(self):
        """
        Probar que no se puede agregar mas de un producto con la
        categoria 'buje' a la lista de materiales de un clisse. 
        """
        # Agregar mas de un buje desde la creacion del clisse.
        with self.assertRaises(ValidationError):
            self.env["hagus.clisse"].create({
                "description": "cl01234",
                "troquel_id": self.troquels[0].id,
                "labels_per_roll": 10,
                "quantity": 15,
                "decrease": 2952.75,
                "handm_cost": .2312,
                "materials_lines_id": [
                    (
                        0,
                        4,
                        {
                            "product_id": self.products[2].id,
                            "cost": .085,
                        }
                    ),
                    (
                        0,
                        4,
                        {
                            "product_id": self.products[3].id,
                            "cost": .37
                        }
                    ),
                    (
                        0,
                        4,
                        {
                            "product_id": self.products[5].id,
                            "cost": 1
                        }
                    ),
                ]
            })
        # Agregar un buje a un clisse que ya lo tiene
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                with f.materials_lines_id.new() as line:
                    line.product_id = self.products[5]

    def test_clisse_state(self):
        """Probar que cuando el campo active es igual a False, el estado del clisse pasa a inactivo"""
        with Form(self.clisse) as f:
            f.active = False
            self.assertEqual(f.state, "inactive")

    def test_rubber_cost(self):
        """Probar que el resultado del costo del Caucho se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(
            clisse.rubber_cost, 210, precision_digits=2), 0)

    def test_negative_cost(self):
        """Probar que el resultado del costo del Negativo se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(
            clisse.negative_cost, 20, precision_digits=2), 0)

    def test_negative_plus_rubber_cost(self):
        """Probar que el resultado del costo Negativo / Caucho se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(
            clisse.negative_plus_rubber_cost, 230, precision_digits=2), 0)

    def test_paper_cost(self):
        """Probar que el resultado del costo del papel se cacula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(
            clisse.paper_cost, 565.93, precision_digits=2), 0)

    def test_print_cost(self):
        """Probar que el resultado del costo de impresion se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(
            clisse.print_cost, 75.14, precision_digits=2), 0)

    def test_coiling_cost(self):
        """Probar que el resultado del costo de embobinado se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.coiling_cost, 2.91, precision_digits=0), 0)

    def test_packing_cost(self):
        """Probar que el resultado del costo de empaquetado se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.packing_cost, 1.5, precision_digits=0), 0)

    def test_total_cost(self):
        """Probar que el resultado del costo total se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.total_cost, 875.55, precision_digits=2), 0)

    def test_expenses(self):
        """Probar que el resultado de los gastos generales se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.expenses, 218.89, precision_digits=2), 0)

    def test_subtotal(self):
        """Probar que el resultado del subtotal se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.subtotal, 1094.44, precision_digits=2), 0)

    def test_total_price(self):
        """Probar que el resultado del precio total se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.total_price, 2188.88, precision_digits=2), 0)

    def test_thousand_price(self):
        """Probar que el resultado del precio por millar se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.thousand_price, 145.93, precision_digits=2), 0)

    def test_check_product_template_id(self):
        """Probar que el clisse no puede tener mas de un producto asociado"""
        clisse = self.clisse
        with self.assertRaises(UserError):
            clisse.write({
                "product_template_ids": [
                    (
                        0,
                        0,
                        {
                            "name": clisse.description,
                            "price": clisse.thousand_price,
                            "categ_id": clisse.product_type.id,
                            "description": clisse.description,
                            "sale_ok": True,
                            "purchase_ok": False,
                            "type": "product",
                            "standard_price": clisse.total_cost,
                            "list_price": clisse.thousand_price,
                            "image_1920": clisse.image_design,
                            "invoice_policy": "order",

                        }
                    )
                ]
            })

    def test_check_quantity(self):
        """Probar que la cantidad del clisse no puede ser un numero menor o igual a cero."""
        clisse = self.clisse
        with self.assertRaises(ValidationError):
            clisse.write({"quantity": 0})
        with self.assertRaises(ValidationError):
            clisse.write({"quantity": -5})

    def test_total_mts(self):
        """Probar que el total de metros se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.total_mts, 190.5, precision_digits=2), 0)

    def test_total_ft(self):
        """Probar que el total de pies se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.total_ft, 625.00, precision_digits=2), 0)

    def test_estimate_msi(self):
        """Probar que el campo de msi estimados se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.estimate_msi, 187.5, precision_digits=2), 0)

    def test_digits_number(self):
        """Probar que el campo Nro de digitos se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.digits_number, .5, precision_digits=2), 0)

    def test_pressmen_times(self):
        """
        Probar que en los campos que representan tiempo, correspondientes a las horas de inicio del montaje,
        y las horas tanto de entrada como de salida de los prensistas; no se pueden introducir valores invalidos.
        """
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.mount_start_time = -1
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.start_pressman_1 = -1
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.start_pressman_2 = -1
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.end_pressman_1 = -1
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.end_pressman_2 = -1
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.mount_start_time = 25
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.start_pressman_1 = 25
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.start_pressman_2 = 25
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.end_pressman_1 = 25
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                f.end_pressman_2 = 25

    def test_clisse_product_creation(self):
        """
        Probar que cuando se genera un clisse, es creado tambien un producto
        que tiene asociado ese clisse, asi como la categoria y la descripcion.
        """
        clisse = self.clisse
        self.assertEqual(bool(clisse.product_template_ids), True)
        product = clisse.product_template_ids[0]
        self.assertEqual(clisse.product_type, product.categ_id)
        self.assertEqual(clisse.description, product.description)

    def test_clisse_product_update(self):
        """
        Probar que cuando se actualiza un clisse, el producto asociado a ese clisse se actualiza tambien.
        """
        self.clisse.write({
            "product_type": self.env["product.category"].search([("name", '=', "Etiqueta")]).id,
            "description": "Clisse Test new Text.",
        })
        clisse = self.clisse
        product = clisse.product_template_ids[0]
        self.assertEqual(clisse.product_type.name, product.categ_id.name)
        self.assertEqual(clisse.description, product.description)

    def test_action_create_sale_order_needs_a_client(self):
        """
        Probar que cuando se ejecuta la accion "action_create_sale_order" sin haber seleccionado antes un
        cliente, se muestra el mensaje de error correspondiente que no permite generar la orden de venta.
        """
        with self.assertRaises(UserError):
            self.clisse.action_create_sale_order()
        self.assertEqual(len(self.clisse.sale_order_ids), 0)

    def test_action_create_sale_order_active_false(self):
        """
        Probar que cuando se ejecuta la accion "action_create_sale_order" y el estado del clisse es inactivo,
        se muestra el mensaje de error correspondiente que no permite generar la orden de venta.
        """
        clisse = self.clisse
        clisse.write({"active": False})
        with self.assertRaises(UserError):
            clisse.action_create_sale_order()
        self.assertEqual(len(clisse.sale_order_ids), 0)

    def test_sale_order_creation(self):
        """
        Probar que cuando se ejecuta la accion "action_create_sale_order" se genera correctamente una orden
        de venta con los datos del producto asociado al clisse y se agrega al campo sale_order_ids del clisse.
        """
        self.clisse.write({"partner_id": 1, "quantity": 500})
        sale_order = self.clisse.action_create_sale_order()
        self.assertEqual(self.env["sale.order"].search([("id", '=', sale_order["res_id"])]),
                         self.clisse.sale_order_ids)

    def test_same_sale_order_creation_twice(self):
        """
        Probar que cuando se intentan crear dos ordenes de venta seguidas con la misma cantidad a producir
        y sin haber confirmado la primera se muestra el mensaje de error correspondiente.
        """
        self.clisse.write({"partner_id": 1, "quantity": 350})
        self.clisse.action_create_sale_order()
        with self.assertRaises(UserError):
            self.clisse.action_create_sale_order()

    def test_action_create_mrp_production_active_false(self):
        """
        Probar que cuando se ejecuta la accion de crear orden de produccion y el campo active es False
        se muestra el mensaje de error correspondiente que no permite generar la orden de produccion.
        """
        clisse = self.clisse
        clisse.write({"active": False})
        with self.assertRaises(UserError):
            clisse.action_create_mrp_production()

    def test_action_create_mrp_production_without_confirmed_sale_order(self):
        """
        Probar que cuando se intenta crear una orden de produccion sin tener antes 
        una orden de venta confirmada del mismo clisse, se muestra el mensaje de
        error correspondiente que no permite generar la orden de produccion.
        """
        clisse = self.clisse
        clisse.write({
            "active": True,
            "state": "draft",
            "partner_id": 1,
        })
        # Probando cuando no existen ordenes de venta.
        for order in clisse.sale_order_ids:
            clisse.write({"sale_order_ids": [(5, order.id)]})
        with self.assertRaises(UserError):
            clisse.action_create_mrp_production()
        # Probando cuando existe una orden de venta sin confirmar.
        clisse.action_create_sale_order()
        with self.assertRaises(UserError):
            clisse.action_create_mrp_production()

    def test_mrp_production_creation(self):
        """
        Probar que cuando se ejecuta la accion "action_create_mrp_production" se genera correctamente una orden
        de produccion con los datos del producto asociado al clisse y se agrega al campo mrp_production_ids del clisse.
        Ademas, el estado del clisse debe pasar a "en produccion".
        """
        clisse = self.clisse
        clisse.write({
            "active": True,
            "state": "draft",
            "partner_id": 1,
        })
        # Borrando ordenes de venta existentes.
        for order in clisse.sale_order_ids:
            clisse.write({"sale_order_ids": [(5, order.id)]})
        # Creando una nueva orden de venta y confirmandola.
        clisse.action_create_sale_order()
        clisse.sale_order_ids.write({"state": "sale"})
        mrp_production = clisse.action_create_mrp_production()
        self.assertEqual(self.env["mrp.production"].search([("id", '=', mrp_production["res_id"])]),
                         self.clisse.mrp_production_ids)
        self.assertEqual(clisse.state, "production")

    def test_coil_id(self):
        """
        Probar que el campo coil_id del modelo Clisse
        solo pueda aceptar productos cuya categoria es bobina.
        """
        clisse = self.clisse
        # Agregando un producto invalido
        with self.assertRaises(ValidationError):
            clisse.write({"coil_id": self.products[0].id})
        # Agregando un producto valido
        clisse.write({"coil_id": self.products[3].id})
        self.assertEqual(self.products[3], clisse.coil_id)
