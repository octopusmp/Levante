from odoo import models
from odoo.http import request

# Kod girilmeden de erisilebilmesi gereken yollar:
# - PIN ekraninin kendisi (sonsuz yonlendirme olmasin diye)
# - Giris / oturum / sifre yollari (admin girebilsin)
# - statik dosyalar ve asset paketleri (PIN ekrani ve giris sayfasi bozulmasin)
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

    def _dispatch(self, endpoint):
        if self._levante_pin_should_block():
            target = request.httprequest.full_path or "/"
            # full_path bazen sonuna '?' ekler; temizleyelim
            if target.endswith("?"):
                target = target[:-1]
            return request.redirect("/pin?redirect=%s" % target)
        return super()._dispatch(endpoint)

    def _levante_pin_should_block(self):
        # Aktif bir request/oturum yoksa dokunma
        if not request or not getattr(request, "session", None):
            return False

        # Bu oturumda kod zaten dogru girilmis
        if request.session.get("levante_pin_ok"):
            return False

        # Giris yapmis kullanicilar (admin/portal) kilidi gormez
        if request.session.uid:
            return False

        icp = request.env["ir.config_parameter"].sudo()

        # Kod tanimli degilse kilit devre disi (kaza ile herkesi disarida birakmayalim)
        code = (icp.get_param("levante_pin.code") or "").strip()
        if not code:
            return False

        # Sadece belirtilen domain korunur
        domain = (icp.get_param("levante_pin.domain") or "").strip()
        if not domain:
            return False
        host = (request.httprequest.host or "").split(":")[0].lower()
        if domain.lower() not in host:
            return False

        # Beyaz listedeki yollar serbest
        path = request.httprequest.path or "/"
        if path.startswith(WHITELIST_PREFIXES):
            return False
        if "/static/" in path:
            return False

        return True
