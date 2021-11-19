# Copyright (C) 2021 Trevi Software (https://trevi.et)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import AccessError
from odoo.tests import common, new_test_user


class TestGroupPayrollManager(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestGroupPayrollManager, cls).setUpClass()

        cls.Partner = cls.env["res.partner"]
        cls.Ticket = cls.env["helpdesk.ticket"]
        cls.User = cls.env["res.users"]

        # Parent Org
        cls.partnerCompany = cls.Partner.create({"name": "Acme Widgets"})

        # Portal User
        cls.partnerPortal = cls.Partner.create(
            {
                "name": "Portal",
                "email": "portal@example.com",
                "parent_id": cls.partnerCompany.id,
                "it_contact": True,
            }
        )
        cls.userPortal = new_test_user(
            cls.env,
            email="portal@example.com",
            login="portal@example.com",
            partner_id=cls.partnerPortal.id,
            groups="base.group_portal",
        )

    def test_helpdesk_ticket_read(self):
        """Has read access to helpdesk.ticket"""

        # Ticket
        ticket = self.Ticket.create(
            {
                "name": "Help",
                "description": "Help",
                "partner_id": self.partnerPortal.id,
            }
        )

        try:
            ticket.with_user(self.userPortal.id).read(["name", "description"])
        except AccessError:
            self.fail("raised an AccessError Exception")

    def test_helpdesk_ticket_nested_parent(self):
        """Has read access through several layers or parents"""

        grandParent = self.Partner.create(
            {
                "name": "Supra Company",
                "is_company": True,
            }
        )
        self.partnerCompany.parent_id = grandParent

        # Ticket
        ticket = self.Ticket.create(
            {
                "name": "Help",
                "description": "Help",
                "partner_id": grandParent.id,
            }
        )

        try:
            ticket.with_user(self.userPortal.id).read(["name", "description"])
        except AccessError:
            self.fail("raised an AccessError Exception")
