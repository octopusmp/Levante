from odoo import fields, models


class EstatePropertyImage(models.Model):
    _name = "estate.property.image"
    _description = "Property Gallery"
    _order = "sequence, id"

    property_id = fields.Many2one(
        "estate.property", required=True, ondelete="cascade"
    )
    image = fields.Image(
        "Photo", required=True, max_width=1200, max_height=800
    )
    sequence = fields.Integer(default=10)
    caption = fields.Char("Caption")
