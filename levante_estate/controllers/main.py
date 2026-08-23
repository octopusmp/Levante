from odoo import http
from odoo.http import request


class EstateController(http.Controller):

    @http.route(
        "/properties",
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def property_list(
        self,
        ptype=None,
        max_price=None,
        min_area=None,
        **kw,
    ):
        website_id = request.website.id
        domain = [
            ("website_id", "=", website_id),
            ("website_published", "=", True),
        ]
        if ptype:
            domain.append(("property_type", "=", ptype))
        if max_price:
            try:
                domain.append(("price", "<=", float(max_price)))
            except ValueError:
                pass
        if min_area:
            try:
                domain.append(("area_m2", ">=", float(min_area)))
            except ValueError:
                pass

        properties = (
            request.env["estate.property"]
            .sudo()
            .search(domain)
        )

        type_choices = [
            ("apartment", "Daire"),
            ("villa", "Villa / Müstakil"),
            ("land", "Arsa"),
            ("commercial", "Ticari"),
            ("office", "Ofis"),
        ]

        return request.render(
            "levante_estate.property_list",
            {
                "properties": properties,
                "type_choices": type_choices,
                "current_type": ptype or "",
                "max_price": max_price or "",
                "min_area": min_area or "",
            },
        )

    @http.route(
        "/property/<int:property_id>-<string:slug>",
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def property_detail(self, property_id, slug, **kw):
        prop = (
            request.env["estate.property"]
            .sudo()
            .browse(property_id)
        )
        if (
            not prop.exists()
            or prop.website_id.id != request.website.id
            or not prop.website_published
        ):
            return request.not_found()

        return request.render(
            "levante_estate.property_detail",
            {
                "prop": prop,
                "video_embed": prop._get_video_embed_url(),
                "map_embed": prop._get_map_embed_url(),
            },
        )
