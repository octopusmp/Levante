import re
from urllib.parse import quote

from odoo import fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property Listing"
    _order = "sequence, id desc"

    name = fields.Char("Title", required=True)
    sequence = fields.Integer(default=10)
    description = fields.Html("Description")
    property_type = fields.Selection(
        [
            ("apartment", "Apartment"),
            ("villa", "Villa / Detached"),
            ("land", "Land"),
            ("commercial", "Commercial"),
            ("office", "Office"),
        ],
        string="Type",
        required=True,
        default="apartment",
    )
    state = fields.Selection(
        [
            ("available", "For Sale"),
            ("reserved", "Reserved"),
            ("sold", "Sold"),
        ],
        string="Status",
        default="available",
        required=True,
    )
    price = fields.Float("Price (USD)", required=True, digits=(15, 0))
    area_m2 = fields.Float("Area (m2)", digits=(7, 1))
    bedrooms = fields.Integer("Bedrooms")
    bathrooms = fields.Integer("Bathrooms")
    address = fields.Char("Address / Area")
    video_url = fields.Char("Video URL (YouTube / Vimeo)")
    cover_image = fields.Image("Cover Photo", max_width=1200, max_height=800)
    image_ids = fields.One2many(
        "estate.property.image", "property_id", string="Gallery"
    )
    agent_id = fields.Many2one("res.partner", string="Agent")
    website_id = fields.Many2one(
        "website", string="Website", required=True,
        default=lambda self: self._default_website(),
    )
    website_published = fields.Boolean("Published on Site", default=True)
    active = fields.Boolean(default=True)

    def _default_website(self):
        ws = self.env["website"].search(
            [("domain", "ilike", "levanteproperty")], limit=1
        )
        return ws or self.env["website"].search([], limit=1, order="id asc")

    def _get_url_slug(self):
        return re.sub(r"[^a-z0-9]+", "-", (self.name or "").lower()).strip("-") or "property"

    def _get_detail_url(self):
        return "/property/%d-%s" % (self.id, self._get_url_slug())

    def _format_price(self):
        return "$ {:,.0f}".format(self.price)

    def _get_video_embed_url(self):
        url = self.video_url or ""
        yt = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_\-]+)", url)
        if yt:
            return "https://www.youtube.com/embed/%s?rel=0" % yt.group(1)
        vm = re.search(r"vimeo\.com/(\d+)", url)
        if vm:
            return "https://player.vimeo.com/video/%s" % vm.group(1)
        return url if ("embed" in url or "player" in url) else None

    def _get_map_embed_url(self):
        if not self.address:
            return None
        return "https://maps.google.com/maps?q=%s&output=embed&z=15" % quote(self.address)

    _TYPE_LABELS = {
        "apartment": "Apartment",
        "villa": "Villa",
        "land": "Land",
        "commercial": "Commercial",
        "office": "Office",
    }
    _STATE_CLASSES = {
        "available": ("For Sale", "success"),
        "reserved":  ("Reserved",  "warning"),
        "sold":      ("Sold",       "danger"),
    }

    def _type_label(self):
        return self._TYPE_LABELS.get(self.property_type, self.property_type)

    def _state_label(self):
        return self._STATE_CLASSES.get(self.state, ("?", "secondary"))[0]

    def _state_class(self):
        return self._STATE_CLASSES.get(self.state, ("?", "secondary"))[1]
