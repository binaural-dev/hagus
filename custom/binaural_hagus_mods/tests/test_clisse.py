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
        """Probar que el resultado de los gastps generales se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(clisse.expenses, 218.89, precision_digits=2), 0)

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
            self.assertEqual(self.clisse.sale_order_ids[-1], 3450)

    def test_sale_order_creation(self):
        """
        Probar que cuando se ejecuta la accion "action_create_sale_order" se genera correctamente una orden
        de venta con los datos del producto asociado al clisse y se agrega al campo sale_order_ids del clisse.
        """
        self.clisse.write({"partner_id": 1, "quantity": 500})
        sale_order = self.clisse.action_create_sale_order()
        self.assertEqual(self.env["sale.order"].search([("id", '=', sale_order["res_id"])]), self.clisse.sale_order_ids[-1])

    def test_same_sale_order_creation_twice(self):
        """
        Probar que cuando se intentan crear dos ordenes de venta seguidas con la misma cantidad a producir
        y sin haber confirmado la primera se muestra el mensaje de error correspondiente.
        """
        with self.assertRaises(UserError):
            self.clisse.write({"partner_id": 1, "quantity": 350})
            self.clisse.action_create_sale_order()
            self.clisse.action_create_sale_order()
