import re
from urllib.parse import quote

from odoo import api, fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Gayrimenkul İlanı"
    _order = "sequence, id desc"

    # ── Temel Bilgiler ────────────────────────────────────────────────────
    name = fields.Char("Başlık", required=True)
    sequence = fields.Integer(default=10)
    description = fields.Html("Açıklama")
    property_type = fields.Selection(
        [
            ("apartment", "Daire"),
            ("villa", "Villa / Müstakil"),
            ("land", "Arsa"),
            ("commercial", "Ticari"),
            ("office", "Ofis"),
        ],
        string="Tür",
        required=True,
        default="apartment",
    )
    state = fields.Selection(
        [
            ("available", "Satışta"),
            ("reserved", "Rezerve"),
            ("sold", "Satıldı"),
        ],
        string="Durum",
        default="available",
        required=True,
    )

    # ── Fiyat ve Özellikler ───────────────────────────────────────────────
    price = fields.Float("Fiyat (₺)", required=True, digits=(15, 0))
    area_m2 = fields.Float("Alan (m²)", digits=(7, 1))
    bedrooms = fields.Integer("Yatak Odası")
    bathrooms = fields.Integer("Banyo")

    # ── Konum ve Medya ────────────────────────────────────────────────────
    address = fields.Char("Adres / Bölge")
    video_url = fields.Char("Video URL (YouTube / Vimeo)")
    cover_image = fields.Image(
        "Kapak Fotoğrafı", max_width=1200, max_height=800
    )
    image_ids = fields.One2many(
        "estate.property.image", "property_id", string="Galeri Fotoğrafları"
    )

    # ── İletişim ve Yayın ─────────────────────────────────────────────────
    agent_id = fields.Many2one("res.partner", string="Sorumlu Ajan")
    website_id = fields.Many2one(
        "website",
        string="Website",
        required=True,
        default=lambda self: self._default_website(),
    )
    website_published = fields.Boolean("Sitede Yayında", default=True)
    active = fields.Boolean(default=True)

    # ── Yardımcı Metodlar ─────────────────────────────────────────────────
    def _default_website(self):
        ws = self.env["website"].search(
            [("domain", "ilike", "levanteproperty")], limit=1
        )
        return ws or self.env["website"].search([], limit=1, order="id asc")

    def _get_url_slug(self):
        slug = re.sub(r"[^a-z0-9]+", "-", (self.name or "").lower()).strip("-")
        return slug or "ilan"

    def _get_detail_url(self):
        return "/property/%d-%s" % (self.id, self._get_url_slug())

    def _format_price(self):
        """1500000 → 1.500.000 ₺"""
        return "{:,.0f} ₺".format(self.price).replace(",", ".")

    def _get_video_embed_url(self):
        url = self.video_url or ""
        yt = re.search(
            r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_\-]+)", url
        )
        if yt:
            return "https://www.youtube.com/embed/%s?rel=0" % yt.group(1)
        vm = re.search(r"vimeo\.com/(\d+)", url)
        if vm:
            return "https://player.vimeo.com/video/%s" % vm.group(1)
        if "embed" in url or "player" in url:
            return url
        return None

    def _get_map_embed_url(self):
        if not self.address:
            return None
        return "https://maps.google.com/maps?q=%s&output=embed&z=15" % quote(
            self.address
        )

    # Tür ve durum etiketleri için yardımcılar
    _TYPE_LABELS = {
        "apartment": "Daire",
        "villa": "Villa",
        "land": "Arsa",
        "commercial": "Ticari",
        "office": "Ofis",
    }
    _STATE_CLASSES = {
        "available": ("Satışta", "success"),
        "reserved": ("Rezerve", "warning"),
        "sold": ("Satıldı", "danger"),
    }

    def _type_label(self):
        return self._TYPE_LABELS.get(self.property_type, self.property_type)

    def _state_label(self):
        return self._STATE_CLASSES.get(self.state, ("?", "secondary"))[0]

    def _state_class(self):
        return self._STATE_CLASSES.get(self.state, ("?", "secondary"))[1]
