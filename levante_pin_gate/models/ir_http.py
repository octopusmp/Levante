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

# Tarayici kapatilip bu sure (ms) icinde acilirsa PIN sorma
# 120000 = 2 dakika. Dilersen degistirebilirsin.
_GRACE_MS = 120000

_PIN_SCRIPT = (
    b"<script>(function(){"
    b"var D='levanteproperty.com';"
    b"if(window.location.hostname.indexOf(D)===-1)return;"
    b"if(window.location.pathname.indexOf('/pin')===0)return;"
    b"var HB='lpg_hb',OK='lpg_ok',SS='lpg_s',G=" + str(_GRACE_MS).encode() + b";"
    b"function go(){window.location.replace('/pin?redirect='+encodeURIComponent(window.location.pathname+window.location.search));}"
    b"function beat(){try{localStorage.setItem(HB,Date.now());}catch(e){}}"
    b"setInterval(beat,30000);"
    b"var ss=sessionStorage.getItem(SS)==='1';"
    b"var ok=localStorage.getItem(OK)==='1';"
    b"var lh=parseInt(localStorage.getItem(HB)||'0',10);"
    b"var fr=(Date.now()-lh)<G;"
    b"if(ss&&ok){beat();return;}"
    b"if(!ss&&ok&&fr){sessionStorage.setItem(SS,'1');beat();return;}"
    b"localStorage.removeItem(OK);localStorage.removeItem(HB);"
    b"var x=new XMLHttpRequest();"
    b"x.open('GET','/pin/clear');"
    b"x.onload=go;x.onerror=go;x.send();"
    b"})()</script>"
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
        response = super()._dispatch(endpoint)
        cls._levante_inject_js(response)
        return response

    @classmethod
    def _levante_inject_js(cls, response):
        """Korumali domain'in HTML yanitlerina JS nabiz kodunu ekle."""
        try:
            if "text/html" not in response.headers.get("Content-Type", ""):
                return
            icp = request.env["ir.config_parameter"].sudo()
            domain = (icp.get_param("levante_pin.domain") or "").strip()
            if not domain:
                return
            host = (request.httprequest.host or "").split(":")[0].lower()
            if domain.lower() not in host:
                return
            data = response.get_data()
            if b"</body>" in data:
                data = data.replace(b"</body>", _PIN_SCRIPT + b"</body>", 1)
            elif b"</html>" in data:
                data = data.replace(b"</html>", _PIN_SCRIPT + b"</html>", 1)
            else:
                data = data + _PIN_SCRIPT
            response.set_data(data)
        except Exception:
            pass

    @classmethod
    def _levante_pin_should_block(cls):
        try:
            if not request or not getattr(request, "session", None):
                return False
            # Sunucu tarafli cookie kontrolu (ilk kalkan)
            if request.httprequest.cookies.get("levante_pin_ok") == "1":
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
            return False
