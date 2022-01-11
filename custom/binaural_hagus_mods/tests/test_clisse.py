from odoo.tests.common import Form, SavepointCase
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import float_compare


@tagged("post_install", "-at_install")
class HagusClisseTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(HagusClisseTestCase, cls).setUpClass()

        cls.categories = [
            cls.env["product.category"].create({
                "name": "Tinta"
            }),
            cls.env["product.category"].create({
                "name": "Etiqueta"
            }),
            cls.env["product.category"].create({
                "name": "Buje"
            }),
            cls.env["product.category"].create({
                "name": "Bobina"
            })
        ]

        cls.products = [
            cls.env["product.product"].create({
                "name": "Tinta Negra",
                "categ_id": cls.categories[0].id
            }),
            cls.env["product.product"].create({
                "name": "Tinta Azul",
                "categ_id": cls.categories[0].id
            }),
            cls.env["product.product"].create({
                "name": "Bushing Test",
                "categ_id": cls.categories[2].id,
            }),
            cls.env["product.product"].create({
                "name": "Coil Test",
                "categ_id": cls.categories[3].id,
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
            "quantity": 15,
            "decrease": 2952.75,
            "handm_cost": .2312,
            "materials_lines_id": [
                (
                    0,
                    4,
                    {
                        "product_id": cls.products[0].id
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": cls.products[1].id
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": cls.products[2].id,
                        "cost": .37
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

    def test_rubber_plus_negative_cost(self):
        """Probar que el resultado del costo Negativo / Caucho se calcula correctamente."""
        clisse = self.clisse
        self.assertEqual(float_compare(
            clisse.rubber_cost, 210, precision_digits=2), 0)

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
