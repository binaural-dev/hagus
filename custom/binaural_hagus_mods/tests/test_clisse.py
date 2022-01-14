import logging
from odoo.tests.common import Form, SavepointCase
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tools import float_compare
_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class HagusClisseTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(HagusClisseTestCase, cls).setUpClass()

        cls.products = [
            cls.env["product.product"].create({
                "name": "Tinta Negra",
                "categ_id": cls.env["product.category"].search([("name", '=', "Tinta")]).id,
            }),
            cls.env["product.product"].create({
                "name": "Tinta Azul",
                "categ_id": cls.env["product.category"].search([("name", '=', "Tinta")]).id,
            }),
            cls.env["product.product"].create({
                "name": "Bushing Test",
                "categ_id": cls.env["product.category"].search([("name", '=', "Buje")]).id,
            }),
            cls.env["product.product"].create({
                "name": "Coil Test",
                "categ_id": cls.env["product.category"].search([("name", '=', "Bobina")]).id,
            }),
            cls.env["product.product"].create({
                "name": "Coil Test 2",
                "categ_id": cls.env["product.category"].search([("name", '=', "Bobina")]).id,
            }),
            cls.env["product.product"].create({
                "name": "Bushing Test 2",
                "categ_id": cls.env["product.category"].search([("name", '=', "Buje")]).id,
            }),
        ]

        cls.troquels = [
            cls.env["hagus.troquel"].create({
                "code": "troqtest1",
                "width_inches": 10,
                "length_inches": 10
            }),
        ]

        cls.clisse = cls.env["hagus.clisse"].create({
            "description": "cli012345",
            "troquel_id": cls.troquels[0].id,
            "labels_per_roll": 10,
            "quantity": 15,
            "decrease": 2952.75,
            "handm_cost": .2312,
            "thousand_cost": 500,
            "materials_lines_id": [
                (
                    0,
                    4,
                    {
                        "product_id": cls.products[0].id,
                        "cost": 1.5,
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": cls.products[1].id,
                        "cost": 2,
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": cls.products[2].id,
                        "cost": .085,
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": cls.products[3].id,
                        "cost": .37
                    }
                ),
            ]
        })

    def test_add_more_than_one_rubber_or_negative_product_to_clisse(self):
        """
        Probar que no se puede agregar mas de un producto con los nombres
        'caucho' o 'negativo' a la lista de materiales de un clisse.
        """
        # Agregar mas de un negativo desde la creacion del clisse.
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
                            "product_id": self.env["product.product"].search([("name", '=', "Negativo")]).id,
                            "cost": 1
                        }
                    ),
                ]
            })
        # Agregar un negativo a un clisse que ya lo tiene.
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                with f.materials_lines_id.new() as line:
                    line.product_id = self.env["product.product"].search(
                        [("name", '=', "Negativo")])

        # Agregar mas de un caucho desde la creacion del clisse.
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
                            "product_id": self.env["product.product"].search([("name", '=', "Caucho")]).id,
                            "cost": 1
                        }
                    ),
                ]
            })
        # Agregar un caucho a un clisse que ya lo tiene.
        with self.assertRaises(ValidationError):
            with Form(self.clisse) as f:
                with f.materials_lines_id.new() as line:
                    line.product_id = self.env["product.product"].search(
                        [("name", '=', "Caucho")])

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
            clisse.print_cost, 75.51, precision_digits=2), 0)

    def test_coiling_cost(self):
        """Probar que el resultado del costo de embobinado se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(
            clisse.coiling_cost, .29, precision_digits=2), 0)

    def test_clisse_product_creation(self):
        """
        Probar que cuando se genera un clisse, es creado tambien un producto
        que tiene asociado ese clisse, asi como el precio, la categoria y la descripcion.
        """
        clisse = self.clisse
        self.assertEqual(bool(clisse.product_template_ids), True)
        product = clisse.product_template_ids[0]
        # self.assertEqual(float_compare(
        # clisse.thousand_cost, product.list_price, precision_digits=2), 0)
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
