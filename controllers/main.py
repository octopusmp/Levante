import time

from markupsafe import escape

from odoo import http
from odoo.http import request

PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="robots" content="noindex,nofollow"/>
<title>Giris</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center;
         font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
         background:#0f172a; color:#e2e8f0; }
  .card { background:#1e293b; padding:40px 32px; border-radius:16px; width:min(92vw,360px);
          box-shadow:0 20px 60px rgba(0,0,0,.45); text-align:center; }
  h1 { font-size:20px; margin:0 0 6px; font-weight:600; }
  p  { font-size:14px; color:#94a3b8; margin:0 0 24px; }
  input[type=password] { width:100%; font-size:30px; letter-spacing:14px; text-align:center;
          padding:14px 12px; border:1px solid #334155; border-radius:12px;
          background:#0f172a; color:#fff; outline:none; }
  input[type=password]:focus { border-color:#6366f1; }
  button { margin-top:20px; width:100%; padding:14px; font-size:16px; font-weight:600;
           border:0; border-radius:12px; background:#6366f1; color:#fff; cursor:pointer; }
  button:hover { background:#4f46e5; }
  .err { color:#f87171; font-size:13px; margin-top:14px; min-height:18px; }
</style>
</head>
<body>
  <form class="card" method="post" action="/pin/verify" autocomplete="off">
    <h1>Bu site korumali</h1>
    <p>Devam etmek icin 4 haneli kodu girin</p>
    <input type="password" name="code" inputmode="numeric" pattern="[0-9]*"
           maxlength="4" autofocus required/>
    <input type="hidden" name="csrf_token" value="%%CSRF%%"/>
    <input type="hidden" name="redirect" value="%%REDIRECT%%"/>
    <button type="submit">Giris</button>
    <div class="err">%%ERROR%%</div>
  </form>
</body>
</html>"""


def _safe_redirect(redirect):
    """Sadece site ici yollara izin ver (acik yonlendirme onlemi)."""
    if not redirect or not redirect.startswith("/") or redirect.startswith("//"):
        return "/"
    return redirect


def _render(redirect, error=""):
    html = (
        PAGE.replace("%%CSRF%%", escape(request.csrf_token()))
        .replace("%%REDIRECT%%", escape(_safe_redirect(redirect)))
        .replace("%%ERROR%%", escape(error))
    )
    return request.make_response(
        html, headers=[("Content-Type", "text/html; charset=utf-8")]
    )


class LevantePinGate(http.Controller):

    @http.route("/pin", type="http", auth="public", sitemap=False)
    def pin_form(self, redirect=None, **kw):
        if request.session.get("levante_pin_ok"):
            return request.redirect(_safe_redirect(redirect))
        return _render(redirect)

    @http.route("/pin/verify", type="http", auth="public", methods=["POST"])
    def pin_verify(self, code=None, redirect=None, **kw):
        icp = request.env["ir.config_parameter"].sudo()
        real = (icp.get_param("levante_pin.code") or "").strip()

        now = time.time()
        fails = request.session.get("levante_pin_fails", 0)
        last = request.session.get("levante_pin_last", 0.0)

        # Basit hiz siniri: 5 hatali denemeden sonra 60 sn bekleme
        if fails >= 5 and (now - last) < 60:
            wait = int(60 - (now - last))
            return _render(redirect, "Cok fazla hatali deneme. %s sn bekleyin." % wait)

        if real and code and code.strip() == real:
            request.session["levante_pin_ok"] = True
            request.session["levante_pin_fails"] = 0
            return request.redirect(_safe_redirect(redirect))

        request.session["levante_pin_fails"] = fails + 1
        request.session["levante_pin_last"] = now
        return _render(redirect, "Hatali kod. Tekrar deneyin.")
