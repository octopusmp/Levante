{
    "name": "Levante PIN Gate",
    "version": "19.0.1.0.0",
    "summary": "Belirli bir website'i 4 haneli ortak bir kodla kilitler",
    "description": """
Levante PIN Gate
================
levanteproperty.com gibi tek bir website'in tamamini, herkes icin ortak
4 haneli bir kod ile korur. Kod girilmeden hicbir sayfa gosterilmez.

- Korunacak domain ve kod, Sistem Parametrelerinden ayarlanir.
- Giris yapmis (admin/portal) kullanicilar kilidi gormez.
- Diger website'ler etkilenmez.
""",
    "category": "Website",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["website"],
    "data": [
        "data/ir_config_parameter.xml",
    ],
    "installable": True,
    "application": False,
}
