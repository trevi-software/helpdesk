# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.myaccount import CustomerPortalHelpdesk
from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortalHelpdesk(CustomerPortalHelpdesk):

    # Override ticket count
    #
    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        domain = [("partner_id", "child_of", partner.id)]
        if partner.it_contact and partner.parent_id:
            domain = [("partner_id", "child_of", partner.commercial_partner_id.id)]
            ticket_count = request.env["helpdesk.ticket"].search_count(domain)
            values["ticket_count"] = ticket_count
        return values

    # XXX - copy this entire function form helpdesk_mgmt/controllers/myaccount.py
    # just to override the domain variable. We should submit a PR to OCA/helpdesk
    # to add a hook: def _get_ticket_domain().
    # 2021-11-19 - added a slight re-factor to the ticket listing
    #
    @http.route(
        ["/my/tickets", "/my/tickets/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_tickets(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        HelpdesTicket = request.env["helpdesk.ticket"]
        partner = request.env.user.partner_id
        domain = [("partner_id", "child_of", partner.id)]
        if partner.it_contact and partner.parent_id:
            domain = [("partner_id", "child_of", partner.commercial_partner_id.id)]

        searchbar_sortings = {
            'number': {'label': _('Reference'), 'order': 'number desc'},
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
            "stage": {"label": _("Stage"), "order": "stage_id"},
            "update": {
                "label": _("Last Stage Update"),
                "order": "last_stage_update desc",
            },
        }
        # search filters
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'open': {'label': _('Open'), 'domain': [('closed_date', '=', False)]},
            'closed': {'label': _('Closed'), 'domain': [('closed_date', '!=', False)]},
        }

        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # default filter by value
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]

        # count for pager
        ticket_count = HelpdesTicket.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tickets",
            url_args={},
            total=ticket_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        tickets = HelpdesTicket.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        values.update(
            {
                "date": date_begin,
                "tickets": tickets,
                "page_name": "ticket",
                "pager": pager,
                "default_url": "/my/tickets",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
            }
        )
        return request.render("helpdesk_mgmt.portal_my_tickets", values)
