from odoo import models
from odoo.http import request

WHITELIST_PREFIXES = (
    "/pin",
    "/web/login",
    "/web/session",
    "/web/reset_password",
    "/web/signup",
    "/web/static",
    "/website/static",
    "/web/assets",
    "/web/image",
    "/favicon.ico",
)


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _dispatch(cls, endpoint):
        if cls._levante_pin_should_block():
            target = request.httprequest.full_path or "/"
            if target.endswith("?"):
                target = target[:-1]
            return request.redirect("/pin?redirect=%s" % target)
        return super()._dispatch(endpoint)

    @classmethod
    def _levante_pin_should_block(cls):
        try:
            if not request or not getattr(request, "session", None):
                return False
            if request.session.get("levante_pin_ok"):
                return False
            if request.session.uid:
                return False

            icp = request.env["ir.config_parameter"].sudo()

            code = (icp.get_param("levante_pin.code") or "").strip()
            if not code:
                return False

            domain = (icp.get_param("levante_pin.domain") or "").strip()
            if not domain:
                return False

            host = (request.httprequest.host or "").split(":")[0].lower()
            if domain.lower() not in host:
                return False

            path = request.httprequest.path or "/"
            if path.startswith(WHITELIST_PREFIXES):
                return False
            if "/static/" in path:
                return False

            return True
        except Exception:
            # Hata durumunda kilidi devreye alma, erişimi engelleme
            return False
