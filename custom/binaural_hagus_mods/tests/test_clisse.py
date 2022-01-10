from odoo.tests.common import Form, SavepointCase
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class HagusClisseTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super (HagusClisseTestCase, cls).setUpClass()

        cls.categories = [
            cls.env["product.category"].create({
                "name": "Tinta"
            }),
            cls.env["product.category"].create({
                "name": "Etiqueta"
            }),
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
        ]

        cls.troquels = [
            cls.env["hagus.troquel"].create({
                "code": "troqtest1",
                "width_inches": 10,
                "length_inches": 10
            }),
        ]

    def test_rubber_plus_negative_cost(self):
        """Probar que el resultado del costo Negativo / Caucho se calculca correctamente."""
        clisse = self.env["hagus.clisse"].create({
            "description": "cli012345",
            "troquel_id": self.troquels[0].id,
            "materials_lines_id": [
                (
                    0,
                    4,
                    {
                        "product_id": self.products[0].id
                    }
                ),
                (
                    0,
                    4,
                    {
                        "product_id": self.products[1].id
                    }
                ),
            ]
        })

        self.assertEqual(clisse.rubber_cost, 210)

